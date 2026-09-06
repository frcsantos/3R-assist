from app.services.oecd_citation import build_oecd_tg_citation, prefer_oecd_tg_citation

SAMPLE = """Test No. 429: SkinSensitisation
Report
OECD Guidelines for the Testing of Chemicals, Section4 •  2 July2026
L o c a l  L y m p h  N o d e  A s s a y
Abstract
The basic principle underlying the Local Lymph Node Assay (LLNA) in mouse is that sensitizers induce a primary proliferation oflymphocytes in the auricular lymph nodes draining the site of chemical application.
In the same series
Report
Test No. 442E: In VitroSkin Sensitisation
2 July 2026• 94 Pages
"""

EXPECTED = (
    "OECD (2026), Test No. 429: Skin Sensitisation: Local Lymph Node Assay, "
    "OECD Guidelines for the Testing of Chemicals, Section 4, OECD Publishing, Paris,"
)


def test_build_oecd_tg_citation_from_scraped_page():
    assert build_oecd_tg_citation(SAMPLE) == EXPECTED


def test_prefer_replaces_short_title():
    assert prefer_oecd_tg_citation("Test No. 429: SkinSensitisation", SAMPLE) == EXPECTED


def test_prefer_keeps_existing_bibliographic_form():
    existing = (
        "OECD (2026), Test No. 429: Skin Sensitisation: Local Lymph Node Assay, "
        "OECD Guidelines for the Testing of Chemicals, Section 4, OECD Publishing, Paris,"
    )
    assert prefer_oecd_tg_citation(existing, SAMPLE) == existing


def test_non_oecd_text_returns_none():
    assert build_oecd_tg_citation("Resolução Normativa CONCEA nº 18/2014") is None
