from app.models.i18n import localized_str, localized_str_list
from app.models.method import Method
from app.services.policy_method_match import (
    _MIN_TEXT_SCORE,
    _raw_tokens,
    normalize_oecd_ref,
    text_for_embedding_score,
)


def _method(**overrides) -> Method:
    base = dict(
        id=38,
        slug="lal-bacterial-endotoxin-test",
        name=localized_str(
            "Bacterial Endotoxins Test",
            "Teste de Endotoxinas Bacterianas",
        ),
        description=localized_str("desc"),
        text_for_embedding=(
            "Bacterial Endotoxins Test (LAL test) is an in vitro method used to "
            "detect or quantify endotoxins of gram-negative bacteria as an "
            "alternative to the rabbit pyrogen test, employing Limulus amebocyte "
            "lysate via gel-clot, turbidimetric, or chromogenic techniques."
        ),
        endpoint_category="pyrogenicity",
        study_domain="pharma",
        source_db="FARMACOPEIA_BR",
        keywords=localized_str_list(
            [
                "LAL",
                "Limulus amebocyte lysate",
                "endotoxin",
                "pyrogenicity",
                "in vitro",
            ],
            [
                "LAL",
                "lisado de amebócito de Limulus",
                "endotoxina",
                "pirogenicidade",
                "in vitro",
            ],
        ),
        active=False,
    )
    base.update(overrides)
    return Method(**base)


def test_normalize_oecd_ref():
    assert normalize_oecd_ref("OECD TG 439") == "TG 439"
    assert normalize_oecd_ref("OECD TG 442E") == "TG 442E"
    assert normalize_oecd_ref("TG 442c") == "TG 442C"
    assert normalize_oecd_ref("GD129") == "GD 129"
    assert normalize_oecd_ref("Farmacopeia Brasileira") is None


def test_raw_tokens_strip_accents():
    tokens = _raw_tokens("Avaliação pirogênica")
    assert "avaliacao" in tokens
    assert "pirogenica" in tokens


def test_lal_extract_scores_above_threshold():
    query = (
        "Farmacopeia Brasileira "
        "Teste de Endotoxina Bacteriana (Farmacopeia Brasileira) "
        "Avaliação da contaminação pirogênica em produtos injetáveis"
    )
    score = text_for_embedding_score(query, _method())
    assert score >= _MIN_TEXT_SCORE


def test_unrelated_method_stays_low():
    query = (
        "Farmacopeia Brasileira "
        "Teste de Endotoxina Bacteriana (Farmacopeia Brasileira) "
        "Avaliação da contaminação pirogênica em produtos injetáveis"
    )
    other = _method(
        id=1,
        slug="draize-eye",
        name=localized_str(
            "Draize Eye Irritation Test",
            "Teste de Irritação Ocular de Draize",
        ),
        text_for_embedding="ocular irritation draize rabbit eye",
        keywords=localized_str_list(
            ["ocular", "irritation"],
            ["ocular", "irritacao"],
        ),
        endpoint_category="ocular_irritation",
    )
    assert text_for_embedding_score(query, other) < _MIN_TEXT_SCORE
