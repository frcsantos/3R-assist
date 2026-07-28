from datetime import date

from app.models.document import Document
from app.models.policy import PolicyDocumentMatchRequest
from app.services.policy_document_match import (
    _MIN_TEXT_SCORE,
    document_match_score,
)


def _document(**overrides) -> Document:
    base = dict(
        id=1,
        slug="concea-rn-18-2014",
        doc_ref="RN 18/2014",
        date=date(2014, 9, 24),
        category="regulation",
        url="https://example.org/rn-18-2014",
    )
    base.update(overrides)
    return Document(**base)


def test_exact_doc_ref_match():
    score, kind = document_match_score(
        PolicyDocumentMatchRequest(document_name="RN 18/2014"),
        _document(),
    )
    assert kind == "doc_ref"
    assert score == 1.0


def test_exact_url_match():
    score, kind = document_match_score(
        PolicyDocumentMatchRequest(url="https://example.org/rn-18-2014"),
        _document(),
    )
    assert kind == "url"
    assert score == 1.0


def test_text_overlap_with_year_bonus():
    score, kind = document_match_score(
        PolicyDocumentMatchRequest(
            document_name="Resolução Normativa CONCEA 18",
            document_date="2014",
            responsible_institution="CONCEA",
        ),
        _document(doc_ref="Resolução Normativa CONCEA nº 18/2014"),
    )
    assert kind == "text"
    assert score >= _MIN_TEXT_SCORE


def test_unrelated_document_stays_low():
    score, _kind = document_match_score(
        PolicyDocumentMatchRequest(
            document_name="OECD TG 439",
            document_date="2010",
        ),
        _document(),
    )
    assert score < _MIN_TEXT_SCORE
