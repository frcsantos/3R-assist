"""Match extracted policy document metadata to catalogue documents."""

from __future__ import annotations

from datetime import date

from app.models.document import Document
from app.models.policy import (
    MatchedDocumentSummary,
    PolicyDocumentMatchCandidate,
    PolicyDocumentMatchRequest,
    PolicyDocumentMatchResponse,
)
from app.repositories.documents import DocumentRepository
from app.services.policy_method_match import (
    _overlap_ratio,
    _raw_tokens,
    _token_keys,
)

_MIN_TEXT_SCORE = 0.15


def _normalize_url(url: str | None) -> str:
    if not url:
        return ""
    text = url.strip().lower()
    for prefix in ("https://", "http://"):
        if text.startswith(prefix):
            text = text[len(prefix) :]
            break
    return text.rstrip("/")


def _year_from_value(value: str | date | None) -> str | None:
    if value is None:
        return None
    text = str(value).strip()
    if not text:
        return None
    if len(text) >= 4 and text[:4].isdigit():
        year = text[:4]
        if year.startswith("19") or year.startswith("20"):
            return year
    return None


def document_match_score(
    request: PolicyDocumentMatchRequest,
    document: Document,
) -> tuple[float, str]:
    name = (request.document_name or "").strip()
    institution = (request.responsible_institution or "").strip()
    url = (request.url or "").strip()
    query = " ".join(part for part in (name, institution, url) if part)
    query_tokens = _raw_tokens(query)

    if name and name.casefold() == document.doc_ref.casefold():
        return 1.0, "doc_ref"

    request_url = _normalize_url(url)
    document_url = _normalize_url(document.url)
    if request_url and document_url and request_url == document_url:
        return 1.0, "url"

    if not query_tokens:
        return 0.0, "text"

    ref_score = _overlap_ratio(query_tokens, _token_keys(document.doc_ref))
    slug_score = _overlap_ratio(
        query_tokens,
        _token_keys(document.slug.replace("-", " ")),
    )
    url_score = (
        _overlap_ratio(query_tokens, _token_keys(document.url or ""))
        if document.url
        else 0.0
    )
    score = (0.55 * ref_score) + (0.30 * slug_score) + (0.15 * url_score)

    request_year = _year_from_value(request.document_date)
    document_year = _year_from_value(document.date)
    if request_year and document_year and request_year == document_year:
        score = min(1.0, score + 0.12)

    if (
        request_url
        and document_url
        and (request_url in document_url or document_url in request_url)
    ):
        score = min(1.0, score + 0.2)

    return round(score, 4), "text"


def _to_summary(document: Document) -> MatchedDocumentSummary:
    return MatchedDocumentSummary(
        id=document.id,
        slug=document.slug,
        doc_ref=document.doc_ref,
        date=document.date.isoformat() if document.date else None,
        category=document.category,
        url=document.url,
    )


class PolicyDocumentMatchService:
    def __init__(self, repository: DocumentRepository) -> None:
        self._repository = repository

    async def match(
        self,
        request: PolicyDocumentMatchRequest,
    ) -> PolicyDocumentMatchResponse:
        has_signal = any(
            (value or "").strip()
            for value in (
                request.document_name,
                request.document_date,
                request.responsible_institution,
                request.url,
            )
        )
        if not has_signal:
            return PolicyDocumentMatchResponse(matches=[])

        candidates = await self._repository.list_all()
        scored: list[tuple[Document, str, float]] = []
        for document in candidates:
            score, match_kind = document_match_score(request, document)
            if score < _MIN_TEXT_SCORE:
                continue
            scored.append((document, match_kind, score))

        scored.sort(key=lambda item: (-item[2], item[0].slug))
        return PolicyDocumentMatchResponse(
            matches=[
                PolicyDocumentMatchCandidate(
                    match_kind=match_kind,
                    score=score,
                    document=_to_summary(document),
                )
                for document, match_kind, score in scored[: request.limit]
            ],
        )
