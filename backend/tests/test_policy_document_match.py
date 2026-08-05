from datetime import date

from app.models.document import Document
from app.models.i18n import localized_str
from app.models.policy import PolicyDocumentMatchRequest
from app.services.policy_document_match import (
    _MIN_TEXT_SCORE,
    document_match_score,
)


def _document(**overrides) -> Document:
    base = dict(
        id=1,
        slug="concea-rn-18-2014",
        doc_citation=localized_str("RN 18/2014"),
        date=date(2014, 9, 24),
        category="regulation",
        url="https://example.org/rn-18-2014",
    )
    base.update(overrides)
    return Document(**base)


def test_exact_doc_citation_match():
    score, kind = document_match_score(
        PolicyDocumentMatchRequest(document_name="RN 18/2014"),
        _document(),
    )
    assert kind == "doc_citation"
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
        _document(
            doc_citation=localized_str(
                "Resolução Normativa CONCEA nº 18/2014"
            )
        ),
    )
    assert kind == "text"
    assert score >= _MIN_TEXT_SCORE


def test_document_number_and_exact_date_outrank_same_year_siblings():
    request = PolicyDocumentMatchRequest(
        document_name="RESOLUÇÃO CONCEA Nº 77, DE 22 DE JULHO DE 2026",
        document_date="2026-07-22",
        responsible_institution=(
            "Conselho Nacional de Controle de Experimentação Animal - CONCEA"
        ),
    )
    doc_77 = _document(
        id=77,
        slug="resolucao-normativa-concea-77",
        doc_citation=localized_str(
            "NORMATIVE RESOLUTION CONCEA No 77",
            "RESOLUÇÃO NORMATIVA CONCEA N° 77",
        ),
        date=date(2026, 7, 22),
        url=(
            "https://www.gov.br/.../resolucao-concea-no-77_2026-"
            "reconhece-metodo-alternativo_fator-c.pdf"
        ),
    )
    doc_75 = _document(
        id=75,
        slug="resolucao-normativa-concea-75",
        doc_citation=localized_str(
            "NORMATIVE RESOLUTION CONCEA No 75",
            "RESOLUÇÃO NORMATIVA CONCEA N° 75",
        ),
        date=date(2026, 1, 22),
        url=(
            "https://www.gov.br/.../resolucao-concea-no-75_2026-"
            "reconhece-metodo-alternativo-diagnostico-de-raiva-animal.pdf"
        ),
    )
    score_77, _ = document_match_score(request, doc_77)
    score_75, _ = document_match_score(request, doc_75)
    assert score_77 > score_75
    assert score_77 >= 0.5


def test_exact_date_scores_higher_than_year_only():
    request = PolicyDocumentMatchRequest(
        document_name="RESOLUÇÃO CONCEA Nº 77",
        document_date="2026-07-22",
    )
    exact = _document(
        slug="resolucao-normativa-concea-77",
        doc_citation=localized_str("RESOLUÇÃO NORMATIVA CONCEA N° 77"),
        date=date(2026, 7, 22),
        url="https://example.org/concea-77",
    )
    same_year = _document(
        id=2,
        slug="resolucao-normativa-concea-77-alt",
        doc_citation=localized_str("RESOLUÇÃO NORMATIVA CONCEA N° 77"),
        date=date(2026, 1, 22),
        url="https://example.org/concea-77-alt",
    )
    exact_score, kind = document_match_score(request, exact)
    year_score, _ = document_match_score(request, same_year)
    assert kind == "text"
    assert exact_score > year_score


def test_unrelated_document_stays_low():
    score, _kind = document_match_score(
        PolicyDocumentMatchRequest(
            document_name="OECD TG 439",
            document_date="2010",
        ),
        _document(),
    )
    assert score < _MIN_TEXT_SCORE
