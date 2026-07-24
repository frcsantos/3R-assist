"""Match extracted policy methods to curated database methods."""

from __future__ import annotations

import re

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


def normalize_oecd_ref(code: str | None) -> str | None:
    if not code:
        return None
    text = code.strip()
    text = re.sub(r"^OECD\s+", "", text, flags=re.IGNORECASE)
    match = _OECD_REF_RE.search(text)
    if not match:
        return None
    return f"{match.group(1).upper()} {match.group(2)}"


def _token_set(text: str) -> set[str]:
    return {token for token in re.findall(r"[a-z0-9]+", text.lower()) if len(token) > 2}


def text_for_embedding_score(query: str, method: Method) -> float:
    query_tokens = _token_set(query)
    if not query_tokens:
        return 0.0

    embedding_tokens = _token_set(method.text_for_embedding)
    name_tokens = _token_set(f"{method.name_en} {method.name_pt}")
    embedding_overlap = len(query_tokens & embedding_tokens)
    name_overlap = len(query_tokens & name_tokens)

    embedding_score = embedding_overlap / len(query_tokens)
    name_score = name_overlap / len(query_tokens)
    return round(min(1.0, (0.75 * embedding_score) + (0.25 * name_score)), 4)


def _to_summary(
    method: Method,
    contexts: list[MethodRegulatoryContext] | None = None,
) -> MatchedMethodSummary:
    return MatchedMethodSummary(
        id=method.id,
        slug=method.slug,
        name_en=method.name_en,
        name_pt=method.name_pt,
        description_en=method.description_en,
        description_pt=method.description_pt,
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
