"""Retrieval service — structured filters plus a composite relevance score.

A method's score combines what the method *is* (its endpoints, routes, test system,
animal use, the procedures it avoids, validation) with how well it reads against the
protocol (semantic similarity when enabled, token overlap otherwise). Components the
protocol gives no information for are left out and the rest are re-weighted, so a
sparse extraction is not punished for what it did not say.
"""

from __future__ import annotations

import logging
import re
import unicodedata
from collections.abc import Callable
from dataclasses import dataclass, field

from app.adapters.embedder import EmbedderAdapter
from app.models.method import Method, MethodRegulatoryContext
from app.models.protocol import (
    ProtocolParameters,
    normalize_application_slug,
    normalize_endpoint_slug,
    normalize_guideline_ref,
    normalize_route_slug,
)
from app.models.recommendation import Recommendation
from app.repositories.methods import MethodRepository
from app.services import vocabulary

logger = logging.getLogger(__name__)

MIN_RESULTS = 3

# Relative importance of each component of the score (they sum to 1).
WEIGHTS: dict[str, float] = {
    "endpoint": 0.30,
    "text": 0.25,
    "animal_use": 0.15,
    "avoided_procedure": 0.10,
    "route": 0.10,
    "application": 0.04,
    "validation": 0.06,
}

# How well a method's endpoints cover the protocol's endpoint.
ENDPOINT_STRENGTH = {"exact": 1.0, "specific": 0.8, "general": 0.6}

# Cosine similarity of all-MiniLM-L6-v2 between a short query and a method text:
# unrelated pairs sit near 0.15, clearly relevant ones near 0.60.
COSINE_FLOOR = 0.15
COSINE_CEILING = 0.60
# With semantic ranking the text component also keeps a lexical share, because exact
# acronyms (LLNA, BCOP, TG numbers) are weak spots of the embedding model.
SEMANTIC_SHARE = 0.65

# Share of the animal-use scale each value represents (1.0 = live animals dosed).
ANIMAL_BURDEN = {
    "none": 0.0,
    "animal_derived_material": 0.15,
    "slaughterhouse_byproduct": 0.2,
    "mixed_or_variable": 0.35,
    "animals_killed_for_tissue": 0.4,
    "embryos_and_larvae": 0.5,
    "live_animals": 1.0,
}
_TEST_SYSTEM_BURDEN = {
    "in_vivo": 1.0,
    "ex_vivo": 0.4,
    "in_vitro": 0.3,
    "in_chemico": 0.0,
    "in_silico": 0.0,
    "in_data": 0.0,
}
# A method that still uses live animals is worth showing when it reduces or refines.
REDUCTION_REFINEMENT_FLOOR = 0.25

VALIDATION_SCORE = {
    "validated": 1.0,
    "recognized": 1.0,
    "partially_validated": 0.6,
    "under_validation": 0.4,
    "not_validated": 0.2,
    "unclear": 0.3,
}

_NON_FILTER_ROUTES = frozenset({"other", "multiple", "not-applicable", "unspecified"})
_NON_ORGANISM_SPECIES = frozenset({"in_vitro", "other"})

_STOPWORDS = frozenset(
    {
        # English
        "the", "and", "for", "with", "from", "that", "this", "were", "was", "are",
        "using", "used", "into", "per", "test", "study",
        # Portuguese
        "com", "para", "por", "uma", "dos", "das", "nos", "nas", "que", "foi",
        "ser", "ensaio", "estudo", "teste",
    }
)


def cosine_similarity(left: list[float], right: list[float]) -> float:
    return sum(a * b for a, b in zip(left, right, strict=True))


def _fold(text: str) -> str:
    """Lower-case and strip accents so 'ativação' and 'ativacao' compare equal."""
    decomposed = unicodedata.normalize("NFKD", text.lower())
    return "".join(char for char in decomposed if not unicodedata.combining(char))


def _token_set(text: str) -> set[str]:
    return {
        token
        for token in re.findall(r"\w+", _fold(text))
        if len(token) > 2 and token not in _STOPWORDS
    }


def _endpoint_label(slug: str) -> str:
    normalized = normalize_endpoint_slug(slug) or slug
    for row in vocabulary.endpoint_rows():
        if row.slug == normalized:
            return row.name.get("en-us") or normalized.replace("-", " ")
    return normalized.replace("-", " ")


def build_query_text(params: ProtocolParameters) -> str:
    """Text embedded for semantic ranking (the methods' texts are English)."""
    parts: list[str] = []
    if params.procedure_text:
        parts.append(params.procedure_text)
    if params.endpoint_category:
        parts.append(_endpoint_label(params.endpoint_category))
    if params.species and params.species not in _NON_ORGANISM_SPECIES:
        parts.append(params.species.replace("_", " "))
    parts.extend(route.replace("-", " ") for route in _filterable_routes(params))
    return " ".join(parts)


# ---------------------------------------------------------------------------
# Matching helpers
# ---------------------------------------------------------------------------


def _match_corpus(method: Method, lang: str | None) -> str:
    parts = [method.text_for_embedding]
    parts.append(method.name.pick(lang) if lang else method.name.joined())
    parts.append(method.description.pick(lang) if lang else method.description.joined())
    keywords = method.keywords.pick(lang) if lang else method.keywords.all_values()
    parts.extend(keywords)
    return " ".join(part for part in parts if part)


def _endpoint_relation(method: Method, params: ProtocolParameters) -> str | None:
    wanted = normalize_endpoint_slug(params.endpoint_category)
    if wanted is None:
        return None
    method_slugs = {
        slug
        for slug in (normalize_endpoint_slug(code) for code in (method.endpoint_codes or []))
        if slug
    }
    return vocabulary.endpoint_relation(wanted, method_slugs)


def _matches_endpoint(method: Method, params: ProtocolParameters) -> bool:
    if params.endpoint_category is None:
        return True
    return _endpoint_relation(method, params) is not None


def _filterable_routes(params: ProtocolParameters) -> list[str]:
    """Routes that participate in soft filtering (catch-all slugs are display-only)."""
    routes: list[str] = []
    for route in params.route or []:
        slug = normalize_route_slug(route) or route
        if slug not in _NON_FILTER_ROUTES and slug not in routes:
            routes.append(slug)
    return routes


def _method_route_slugs(method: Method) -> set[str] | None:
    """Routes the method applies to; None when it is route-independent (e.g. in vitro)."""
    codes = method.route_codes or []
    if codes:
        return {normalize_route_slug(code) or code for code in codes}
    if method.routes_applicable is None:
        return None
    return set()


def _matches_route(method: Method, params: ProtocolParameters) -> bool:
    routes = _filterable_routes(params)
    if not routes:
        return True
    method_slugs = _method_route_slugs(method)
    if method_slugs is None:
        return True
    return any(route in method_slugs for route in routes)


def _apply_filters(
    methods: list[Method],
    params: ProtocolParameters,
    *,
    endpoint: bool,
    route: bool,
) -> list[Method]:
    filtered: list[Method] = []
    for method in methods:
        if endpoint and not _matches_endpoint(method, params):
            continue
        if route and not _matches_route(method, params):
            continue
        filtered.append(method)
    return filtered


def _is_current_method(method: Method, params: ProtocolParameters) -> bool:
    """The protocol already follows this method's guideline (nothing to suggest)."""
    wanted = normalize_guideline_ref(params.guideline_ref)
    have = normalize_guideline_ref(method.oecd_ref)
    return bool(wanted and have and wanted.casefold() == have.casefold())


# ---------------------------------------------------------------------------
# Score components (each returns 0..1, or None when it does not apply)
# ---------------------------------------------------------------------------


def _endpoint_component(method: Method, params: ProtocolParameters) -> float | None:
    if params.endpoint_category is None:
        return None
    relation = _endpoint_relation(method, params)
    return ENDPOINT_STRENGTH.get(relation, 0.0) if relation else 0.0


def _route_component(method: Method, params: ProtocolParameters) -> float | None:
    routes = _filterable_routes(params)
    if not routes:
        return None
    method_slugs = _method_route_slugs(method)
    if method_slugs is None:
        return 0.5  # route-independent method: neither a match nor a mismatch
    return 1.0 if any(route in method_slugs for route in routes) else 0.0


def _application_component(method: Method, params: ProtocolParameters) -> float:
    wanted = normalize_application_slug(params.application)
    codes = {normalize_application_slug(code) or code for code in (method.application_codes or [])}
    return 1.0 if not codes or wanted in codes else 0.0


def _validation_component(method: Method) -> float:
    return VALIDATION_SCORE.get(method.validation_status or "", 0.3)


def _protocol_burden(params: ProtocolParameters) -> float:
    """How much live-animal use the protocol involves (1.0 when not stated)."""
    systems = set(params.test_system or [])
    if "in_vivo" in systems:
        return 1.0
    if systems:
        return max(_TEST_SYSTEM_BURDEN[system] for system in systems)
    if params.species == "in_vitro":
        return _TEST_SYSTEM_BURDEN["in_vitro"]
    return 1.0


def _method_burden(method: Method) -> float | None:
    if method.animal_use in ANIMAL_BURDEN:
        return ANIMAL_BURDEN[method.animal_use]
    systems = [s for s in (method.test_system or []) if s in _TEST_SYSTEM_BURDEN]
    if systems:
        return max(_TEST_SYSTEM_BURDEN[system] for system in systems)
    return None


def _animal_use_component(method: Method, params: ProtocolParameters) -> float:
    """Animal use the method saves relative to the protocol (the point of the tool)."""
    protocol = _protocol_burden(params)
    burden = _method_burden(method)
    if burden is None:
        return 0.5
    gain = max(0.0, protocol - burden)
    keeps_animals = burden >= protocol
    if (
        keeps_animals
        and protocol >= 0.5
        and any(method.has_three_r(r) for r in ("reduction", "refinement"))
    ):
        gain = max(gain, REDUCTION_REFINEMENT_FLOOR)
    return min(1.0, gain)


def _localized_texts(value) -> list[str]:
    if isinstance(value, dict):
        return [text for text in value.values() if isinstance(text, str)]
    return [value] if isinstance(value, str) else []


def _avoided_procedure_component(method: Method, params: ProtocolParameters) -> float:
    """Does the method explicitly stand in for what the protocol is doing?"""
    wanted_ref = normalize_guideline_ref(params.guideline_ref)
    tokens = _token_set(params.procedure_text or "")
    best = 0.0
    for item in method.animal_procedures_avoided or []:
        if not isinstance(item, dict):
            continue
        ref = normalize_guideline_ref(item.get("oecd_ref"))
        if wanted_ref and ref and wanted_ref.casefold() == ref.casefold():
            return 1.0
        species = item.get("species")
        if species and params.species and species == params.species:
            best = max(best, 0.6)
        overlap = len(tokens & _token_set(" ".join(_localized_texts(item.get("name")))))
        if overlap >= 2:
            best = max(best, min(0.9, 0.4 + 0.1 * overlap))
    return best


def _lexical_component(method: Method, params: ProtocolParameters, lang: str | None) -> float | None:
    query = _token_set(params.procedure_text or "")
    if not query:
        return None
    overlap = len(query & _token_set(_match_corpus(method, lang)))
    return min(1.0, overlap / min(len(query), 6))


def _semantic_component(method: Method, query_vector: list[float] | None) -> float | None:
    if query_vector is None or not method.embedding_json:
        return None
    if len(query_vector) != len(method.embedding_json):
        # Stub embedder (EMBEDDING_MODEL unset) or a model swapped without re-embedding.
        logger.warning("Embedding size mismatch for %s; using token overlap", method.slug)
        return None
    cosine = cosine_similarity(query_vector, method.embedding_json)
    span = COSINE_CEILING - COSINE_FLOOR
    return max(0.0, min(1.0, (cosine - COSINE_FLOOR) / span))


@dataclass
class MethodScore:
    score: float
    components: dict[str, float] = field(default_factory=dict)
    matched_params: list[str] = field(default_factory=list)


def score_method(
    method: Method,
    params: ProtocolParameters,
    lang: str | None = None,
    query_vector: list[float] | None = None,
) -> MethodScore:
    lexical = _lexical_component(method, params, lang)
    semantic = _semantic_component(method, query_vector)
    if semantic is not None and lexical is not None:
        text = SEMANTIC_SHARE * semantic + (1 - SEMANTIC_SHARE) * lexical
    else:
        text = semantic if semantic is not None else lexical

    components: dict[str, float | None] = {
        "endpoint": _endpoint_component(method, params),
        "text": text,
        "animal_use": _animal_use_component(method, params),
        "avoided_procedure": _avoided_procedure_component(method, params),
        "route": _route_component(method, params),
        "application": _application_component(method, params),
        "validation": _validation_component(method),
    }
    applicable = {name: value for name, value in components.items() if value is not None}
    total_weight = sum(WEIGHTS[name] for name in applicable)
    score = sum(WEIGHTS[name] * value for name, value in applicable.items()) / total_weight
    if _is_current_method(method, params):
        score *= 0.5

    return MethodScore(
        score=min(1.0, round(score, 4)),
        components={name: round(value, 4) for name, value in applicable.items()},
        matched_params=_matched_params(applicable),
    )


def _matched_params(components: dict[str, float]) -> list[str]:
    matched: list[str] = []
    if components.get("endpoint", 0) > 0:
        matched.append("endpoint_category")
    if components.get("route", 0) >= 1.0:
        matched.append("route")
    if components.get("application", 0) >= 1.0:
        matched.append("application")
    if components.get("avoided_procedure", 0) >= 0.6:
        matched.append("avoided_procedure")
    if components.get("animal_use", 0) >= 0.5:
        matched.append("animal_use")
    return matched


def filter_only_score(
    method: Method,
    params: ProtocolParameters,
    lang: str | None = None,
) -> float:
    """Score without embeddings (token overlap only)."""
    return score_method(method, params, lang=lang).score


def _build_recommendations(
    scored: list[tuple[Method, MethodScore]],
    contexts_by_method: dict[int, list[MethodRegulatoryContext]],
) -> list[Recommendation]:
    scored.sort(key=lambda item: (-item[1].score, item[0].slug))
    return [
        Recommendation(
            method=method,
            regulatory_contexts=contexts_by_method.get(method.id, []),
            rank=index,
            score=result.score,
            matched_params=result.matched_params,
            score_breakdown=result.components,
        )
        for index, (method, result) in enumerate(scored, start=1)
    ]


class RetrievalService:
    def __init__(
        self,
        repository: MethodRepository,
        embedder: EmbedderAdapter,
        *,
        semantic_ranking: bool = False,
    ) -> None:
        self._repository = repository
        self._embedder = embedder
        self._semantic_ranking = semantic_ranking

    async def search(
        self,
        params: ProtocolParameters,
        lang: str | None = None,
    ) -> tuple[list[Recommendation], str | None]:
        methods, contexts_by_method = await self._repository.list_active_with_contexts()
        if not methods:
            return [], None

        query_vector = self._query_vector(methods, params)
        return self._search_with_relaxation(
            methods,
            params,
            lambda candidates: self._rank(candidates, params, contexts_by_method, lang, query_vector),
        )

    def _query_vector(
        self, methods: list[Method], params: ProtocolParameters
    ) -> list[float] | None:
        if not self._semantic_ranking:
            return None
        if not any(method.embedding_json for method in methods):
            logger.warning("Semantic ranking is on but no method has an embedding")
            return None
        query_text = build_query_text(params)
        return self._embedder.embed(query_text) if query_text.strip() else None

    @staticmethod
    def _rank(
        methods: list[Method],
        params: ProtocolParameters,
        contexts_by_method: dict[int, list[MethodRegulatoryContext]],
        lang: str | None,
        query_vector: list[float] | None,
    ) -> list[Recommendation]:
        scored = [
            (method, score_method(method, params, lang=lang, query_vector=query_vector))
            for method in methods
        ]
        return _build_recommendations(scored, contexts_by_method)

    @staticmethod
    def _search_with_relaxation(
        candidates: list[Method],
        params: ProtocolParameters,
        rank: Callable[[list[Method]], list[Recommendation]],
    ) -> tuple[list[Recommendation], str | None]:
        relaxation: str | None = None

        ranked = rank(_apply_filters(candidates, params, endpoint=True, route=True))

        if len(ranked) < MIN_RESULTS:
            without_route = rank(_apply_filters(candidates, params, endpoint=True, route=False))
            if len(without_route) > len(ranked):  # only worth flagging if it added methods
                relaxation = "route_filter_relaxed"
                ranked = without_route

        if not ranked:
            # Nothing matches the endpoint: show the closest by text rather than nothing.
            # (If some methods do match, a short list beats padding it with unrelated ones.)
            relaxation = "endpoint_and_route_filters_relaxed"
            ranked = rank(candidates)[:MIN_RESULTS]

        if relaxation:
            logger.info("Retrieval filter relaxation applied: %s", relaxation)

        return ranked, relaxation
