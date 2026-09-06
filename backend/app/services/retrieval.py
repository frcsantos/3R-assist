"""Retrieval service — filter-based matching (MVP) or semantic search."""

from __future__ import annotations

import logging
from collections.abc import Callable

from app.adapters.embedder import EmbedderAdapter
from app.models.method import Method, MethodRegulatoryContext
from app.models.protocol import ProtocolParameters, normalize_endpoint_slug, normalize_route_slug, normalize_application_slug
from app.models.recommendation import Recommendation
from app.repositories.methods import MethodRepository

logger = logging.getLogger(__name__)

MIN_RESULTS = 3


def build_query_text(params: ProtocolParameters) -> str:
    parts: list[str] = []
    if params.endpoint_category:
        parts.append(params.endpoint_category)
    if params.procedure_text:
        parts.append(params.procedure_text)
    if params.application:
        parts.append(params.application)
    if params.route:
        parts.extend(params.route)
    return " ".join(parts)


def cosine_similarity(left: list[float], right: list[float]) -> float:
    return sum(a * b for a, b in zip(left, right, strict=True))


def _token_set(text: str) -> set[str]:
    return {token for token in text.lower().split() if len(token) > 2}


def filter_only_score(
    method: Method,
    params: ProtocolParameters,
    lang: str | None = None,
) -> float:
    """Heuristic score for MVP validation without embedding models."""
    score = 0.5
    score += 0.15 * len(_matched_params(method, params))
    if params.procedure_text:
        overlap = len(
            _token_set(params.procedure_text) & _token_set(_match_corpus(method, lang))
        )
        score += min(0.35, overlap * 0.05)
    return min(1.0, round(score, 4))


def _match_corpus(method: Method, lang: str | None) -> str:
    parts = [method.text_for_embedding]
    parts.append(method.name.pick(lang) if lang else method.name.joined())
    parts.append(method.description.pick(lang) if lang else method.description.joined())
    keywords = method.keywords.pick(lang) if lang else method.keywords.all_values()
    parts.extend(keywords)
    return " ".join(part for part in parts if part)


def _matches_endpoint(method: Method, params: ProtocolParameters) -> bool:
    if params.endpoint_category is None:
        return True
    wanted = normalize_endpoint_slug(params.endpoint_category)
    return wanted in {
        normalize_endpoint_slug(code) for code in (method.endpoint_codes or [])
    }


_NON_FILTER_ROUTES = frozenset(
    {"other", "multiple", "not-applicable", "unspecified"}
)


def _filterable_routes(params: ProtocolParameters) -> list[str]:
    """Routes that participate in soft filtering (catch-all slugs are display-only)."""
    routes: list[str] = []
    for route in params.route or []:
        slug = normalize_route_slug(route) or route
        if slug not in _NON_FILTER_ROUTES and slug not in routes:
            routes.append(slug)
    return routes


def _method_route_slugs(method: Method) -> set[str] | None:
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


def _matched_params(method: Method, params: ProtocolParameters) -> list[str]:
    matched: list[str] = []
    if params.endpoint_category and normalize_endpoint_slug(
        params.endpoint_category
    ) in {
        normalize_endpoint_slug(code) for code in (method.endpoint_codes or [])
    }:
        matched.append("endpoint_category")
    routes = _filterable_routes(params)
    method_slugs = _method_route_slugs(method)
    if routes and (method_slugs is None or any(route in method_slugs for route in routes)):
        matched.append("route")
    wanted_app = normalize_application_slug(params.application) if params.application else None
    app_codes = {
        normalize_application_slug(code) or code
        for code in (method.application_codes or [])
    }
    if wanted_app and (not app_codes or wanted_app in app_codes):
        matched.append("application")
    return matched


def _build_recommendations(
    scored: list[tuple[Method, float]],
    params: ProtocolParameters,
    contexts_by_method: dict[int, list[MethodRegulatoryContext]],
) -> list[Recommendation]:
    scored.sort(key=lambda item: (-item[1], item[0].slug))
    return [
        Recommendation(
            method=method,
            regulatory_contexts=contexts_by_method.get(method.id, []),
            rank=index,
            score=score,
            matched_params=_matched_params(method, params),
        )
        for index, (method, score) in enumerate(scored, start=1)
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

        if self._semantic_ranking:
            return self._search_semantic(methods, params, contexts_by_method)
        return self._search_filter_only(methods, params, contexts_by_method, lang=lang)

    def _search_with_relaxation(
        self,
        candidates: list[Method],
        params: ProtocolParameters,
        contexts_by_method: dict[int, list[MethodRegulatoryContext]],
        rank: Callable[
            [list[Method], ProtocolParameters, dict[int, list[MethodRegulatoryContext]]],
            list[Recommendation],
        ],
    ) -> tuple[list[Recommendation], str | None]:
        relaxation: str | None = None

        filtered = _apply_filters(candidates, params, endpoint=True, route=True)
        ranked = rank(filtered, params, contexts_by_method)

        if len(ranked) < MIN_RESULTS:
            relaxation = "route_filter_relaxed"
            filtered = _apply_filters(candidates, params, endpoint=True, route=False)
            ranked = rank(filtered, params, contexts_by_method)

        if len(ranked) < MIN_RESULTS:
            relaxation = "endpoint_and_route_filters_relaxed"
            ranked = rank(candidates, params, contexts_by_method)[:MIN_RESULTS]

        if relaxation:
            logger.info("Retrieval filter relaxation applied: %s", relaxation)

        return ranked, relaxation

    def _search_filter_only(
        self,
        methods: list[Method],
        params: ProtocolParameters,
        contexts_by_method: dict[int, list[MethodRegulatoryContext]],
        lang: str | None = None,
    ) -> tuple[list[Recommendation], str | None]:
        return self._search_with_relaxation(
            methods,
            params,
            contexts_by_method,
            lambda filtered, p, contexts: self._rank_filter_only(
                filtered, p, contexts, lang=lang
            ),
        )

    def _search_semantic(
        self,
        methods: list[Method],
        params: ProtocolParameters,
        contexts_by_method: dict[int, list[MethodRegulatoryContext]],
    ) -> tuple[list[Recommendation], str | None]:
        scorable = [method for method in methods if method.embedding_json]
        if not scorable:
            return [], None

        query_text = build_query_text(params)
        if not query_text.strip():
            return [], None

        query_vector = self._embedder.embed(query_text)
        return self._search_with_relaxation(
            scorable,
            params,
            contexts_by_method,
            lambda filtered, p, contexts: self._rank_semantic(
                filtered, query_vector, p, contexts
            ),
        )

    def _rank_filter_only(
        self,
        methods: list[Method],
        params: ProtocolParameters,
        contexts_by_method: dict[int, list[MethodRegulatoryContext]],
        lang: str | None = None,
    ) -> list[Recommendation]:
        scored = [
            (method, filter_only_score(method, params, lang=lang)) for method in methods
        ]
        return _build_recommendations(scored, params, contexts_by_method)

    def _rank_semantic(
        self,
        methods: list[Method],
        query_vector: list[float],
        params: ProtocolParameters,
        contexts_by_method: dict[int, list[MethodRegulatoryContext]],
    ) -> list[Recommendation]:
        scored: list[tuple[Method, float]] = []
        for method in methods:
            if not method.embedding_json:
                continue
            score = round(cosine_similarity(query_vector, method.embedding_json), 4)
            scored.append((method, score))
        return _build_recommendations(scored, params, contexts_by_method)
