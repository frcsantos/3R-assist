"""Match extracted policy methods to curated database methods."""

from __future__ import annotations

import re
import unicodedata

from app.models.method import Method, MethodRegulatoryContext
from app.models.policy import (
    MatchedMethodSummary,
    PolicyMethodMatchCandidate,
    PolicyMethodMatchRequest,
    PolicyMethodMatchResponse,
)
from app.repositories.methods import MethodRepository

_OECD_REF_RE = re.compile(r"\b(TG|GD)\s*(\d{3,4})\b", re.IGNORECASE)
_MIN_TEXT_SCORE = 0.15
_PLURAL_2 = frozenset({"as", "es", "os", "is"})


def normalize_oecd_ref(code: str | None) -> str | None:
    if not code:
        return None
    text = code.strip()
    text = re.sub(r"^OECD\s+", "", text, flags=re.IGNORECASE)
    match = _OECD_REF_RE.search(text)
    if not match:
        return None
    return f"{match.group(1).upper()} {match.group(2)}"


def _strip_accents(text: str) -> str:
    decomposed = unicodedata.normalize("NFD", text)
    return "".join(char for char in decomposed if unicodedata.category(char) != "Mn")


def _raw_tokens(text: str) -> set[str]:
    normalized = _strip_accents(text).lower()
    return {
        token
        for token in re.findall(r"[a-z0-9]+", normalized)
        if len(token) > 2
    }


def _match_keys(token: str) -> set[str]:
    """Soft keys for light plural/suffix and prefix folding (EN/PT)."""
    keys = {token}
    if len(token) > 4 and token.endswith("s") and not token.endswith("ss"):
        keys.add(token[:-1])
    if len(token) > 5 and token[-2:] in _PLURAL_2:
        stem = token[:-2]
        keys.add(stem)
        keys.add(stem + token[-2])
    if len(token) > 5 and token[-1] in "aeiou":
        keys.add(token[:-1])
    if len(token) >= 6:
        keys.add(token[:6])
    return keys


def _token_keys(text: str) -> set[str]:
    keys: set[str] = set()
    for token in _raw_tokens(text):
        keys |= _match_keys(token)
    return keys


def _overlap_ratio(query_tokens: set[str], candidate_keys: set[str]) -> float:
    if not query_tokens:
        return 0.0
    matched = sum(
        1 for token in query_tokens if _match_keys(token) & candidate_keys
    )
    return matched / len(query_tokens)


def text_for_embedding_score(query: str, method: Method) -> float:
    query_tokens = _raw_tokens(query)
    if not query_tokens:
        return 0.0

    embedding_score = _overlap_ratio(
        query_tokens, _token_keys(method.text_for_embedding)
    )
    name_score = _overlap_ratio(
        query_tokens,
        _token_keys(method.name.joined()),
    )
    keyword_text = " ".join(method.keywords.all_values())
    keyword_score = (
        _overlap_ratio(query_tokens, _token_keys(keyword_text))
        if keyword_text.strip()
        else 0.0
    )
    return round(
        min(
            1.0,
            (0.55 * embedding_score) + (0.30 * name_score) + (0.15 * keyword_score),
        ),
        4,
    )


def _to_summary(
    method: Method,
    contexts: list[MethodRegulatoryContext] | None = None,
) -> MatchedMethodSummary:
    return MatchedMethodSummary(
        id=method.id,
        slug=method.slug,
        name=method.name,
        description=method.description,
        text_for_embedding=method.text_for_embedding,
        endpoint_category=method.endpoint_category,
        study_domain=method.study_domain,
        oecd_ref=method.oecd_ref,
        source_db=method.source_db,
        active=method.active,
        regulatory_contexts=contexts or [],
    )


class PolicyMethodMatchService:
    def __init__(self, repository: MethodRepository) -> None:
        self._repository = repository

    async def match(
        self,
        request: PolicyMethodMatchRequest,
    ) -> PolicyMethodMatchResponse:
        normalized = normalize_oecd_ref(request.code)
        if normalized:
            primary = await self._repository.find_by_oecd_ref(
                normalized,
                include_inactive=True,
            )
            if primary:
                return PolicyMethodMatchResponse(
                    normalized_oecd_ref=normalized,
                    matches=await self._candidates_with_contexts(
                        [
                            (method, "oecd_ref", 1.0)
                            for method in primary[: request.limit]
                        ]
                    ),
                )

        query = " ".join(
            part
            for part in (request.code, request.name, request.purpose or "")
            if part and part.strip()
        )
        candidates = await self._repository.list_for_text_match(include_inactive=True)
        scored: list[tuple[Method, str, float]] = []
        for method in candidates:
            score = text_for_embedding_score(query, method)
            if score < _MIN_TEXT_SCORE:
                continue
            scored.append((method, "text_for_embedding", score))

        scored.sort(key=lambda item: (-item[2], item[0].slug))
        return PolicyMethodMatchResponse(
            normalized_oecd_ref=normalized,
            matches=await self._candidates_with_contexts(scored[: request.limit]),
        )

    async def _candidates_with_contexts(
        self,
        scored: list[tuple[Method, str, float]],
    ) -> list[PolicyMethodMatchCandidate]:
        if not scored:
            return []
        contexts_by_id = await self._repository.contexts_by_method_ids(
            [method.id for method, _, _ in scored]
        )
        return [
            PolicyMethodMatchCandidate(
                match_kind=match_kind,
                score=score,
                method=_to_summary(method, contexts_by_id.get(method.id, [])),
            )
            for method, match_kind, score in scored
        ]
