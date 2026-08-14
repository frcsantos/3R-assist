"""Match extracted policy document metadata to catalogue documents."""

from __future__ import annotations

import re
from datetime import date, datetime

from app.models.document import Document
from app.models.i18n import LocalizedStr
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
# Short digit runs (e.g. "77") are dropped by _raw_tokens (len > 2); keep them here.
_NUMBER_RE = re.compile(r"\d+")


def _normalize_url(url: str | None) -> str:
    if not url:
        return ""
    text = url.strip().lower()
    for prefix in ("https://", "http://"):
        if text.startswith(prefix):
            text = text[len(prefix) :]
            break
    return text.rstrip("/")


def _number_tokens(text: str | None) -> set[str]:
    if not text:
        return set()
    return set(_NUMBER_RE.findall(str(text)))


def _doc_tokens(text: str | None) -> set[str]:
    """Word tokens plus digit runs (including short numbers like 18 / 77)."""
    if not text:
        return set()
    return _raw_tokens(text) | _number_tokens(text)


def _doc_token_keys(text: str | None) -> set[str]:
    if not text:
        return set()
    return _token_keys(text) | _number_tokens(text)


def _parse_date(value: str | date | None) -> date | None:
    if value is None:
        return None
    if isinstance(value, date):
        return value
    text = str(value).strip()
    if not text:
        return None
    for fmt, size in (
        ("%Y-%m-%d", 10),
        ("%Y/%m/%d", 10),
        ("%d/%m/%Y", 10),
        ("%d-%m-%Y", 10),
        ("%Y", 4),
    ):
        try:
            return datetime.strptime(text[:size], fmt).date()
        except ValueError:
            continue
    return None


def _date_bonus(request_date: str | date | None, document_date: date | None) -> float:
    """Prefer exact / month match over year-only (shared by many CONCEA RNs)."""
    req = _parse_date(request_date)
    doc = document_date if isinstance(document_date, date) else _parse_date(document_date)
    if req and doc:
        if req == doc:
            return 0.28
        if req.year == doc.year and req.month == doc.month:
            return 0.18
        if req.year == doc.year:
            return 0.08
        return 0.0
    req_year = None
    if req:
        req_year = str(req.year)
    elif request_date is not None:
        text = str(request_date).strip()
        if len(text) >= 4 and text[:4].isdigit() and text[:4].startswith(("19", "20")):
            req_year = text[:4]
    doc_year = str(doc.year) if doc else None
    if req_year and doc_year and req_year == doc_year:
        return 0.08
    return 0.0


def _number_bonus(query_numbers: set[str], candidate_text: str) -> float:
    """Boost when resolution / id numbers from the query appear on the candidate."""
    if not query_numbers:
        return 0.0
    candidate_numbers = _number_tokens(candidate_text)
    if not candidate_numbers:
        return 0.0
    matched = query_numbers & candidate_numbers
    if not matched:
        return 0.0
    # Prefer short non-year digits (document numbers) over shared years.
    identity = {
        n
        for n in matched
        if not (len(n) == 4 and n.startswith(("19", "20")))
    }
    if identity:
        return min(0.35, 0.22 + 0.05 * len(identity))
    return 0.06 * (len(matched) / len(query_numbers))


def _localized_text(value: LocalizedStr | None, lang: str | None) -> str:
    if value is None:
        return ""
    if lang:
        picked = value.pick(lang).strip()
        if picked:
            return picked
    return value.joined()


def document_match_score(
    request: PolicyDocumentMatchRequest,
    document: Document,
) -> tuple[float, str]:
    name = (request.document_name or "").strip()
    institution = (request.responsible_institution or "").strip()
    url = (request.url or "").strip()
    query = " ".join(part for part in (name, institution, url) if part)
    # Numbers from name/date/url only — institution text rarely carries doc ids
    # and would dilute identity matching.
    query_numbers = _number_tokens(
        " ".join(part for part in (name, request.document_date or "", url) if part)
    )
    query_tokens = _doc_tokens(query) | query_numbers
    citation = document.doc_citation
    citation_texts = [
        text for text in (citation.en_us, citation.pt_br) if text.strip()
    ]
    citation_text = _localized_text(citation, request.lang)

    if name:
        name_cf = name.casefold()
        if any(name_cf == text.casefold() for text in citation_texts):
            return 1.0, "doc_citation"

    request_url = _normalize_url(url)
    document_url = _normalize_url(document.url)
    if request_url and document_url and request_url == document_url:
        return 1.0, "url"

    if not query_tokens:
        return 0.0, "text"

    slug_text = document.slug.replace("-", " ")
    institution_text = _localized_text(document.institution, request.lang)
    ref_score = _overlap_ratio(query_tokens, _doc_token_keys(citation_text))
    slug_score = _overlap_ratio(query_tokens, _doc_token_keys(slug_text))
    institution_score = (
        _overlap_ratio(query_tokens, _doc_token_keys(institution_text))
        if institution_text
        else 0.0
    )
    url_score = (
        _overlap_ratio(query_tokens, _doc_token_keys(document.url or ""))
        if document.url
        else 0.0
    )
    score = (
        (0.45 * ref_score)
        + (0.20 * slug_score)
        + (0.15 * institution_score)
        + (0.10 * url_score)
    )

    candidate_number_text = " ".join(
        part
        for part in (
            citation_text,
            slug_text,
            institution_text,
            document.url or "",
        )
        if part
    )
    score = min(1.0, score + _number_bonus(query_numbers, candidate_number_text))
    score = min(1.0, score + _date_bonus(request.document_date, document.date))

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
        doc_citation=document.doc_citation,
        date=document.date.isoformat() if document.date else None,
        categories=list(document.categories),
        institution=document.institution,
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
