import pytest

from app.services import article_pipeline as ap


def test_split_methods_stays_inside_until_stop_heading():
    sections = [
        ("Introduction", ["intro"]),
        ("Materials and Methods", ["m1"]),
        ("Drug administration", ["m2"]),
        ("Results", ["r1"]),
    ]
    methods, other = ap.split_methods(sections)
    assert methods == ["[Materials and Methods] m1", "[Drug administration] m2"]
    assert other == ["[Introduction] intro", "[Results] r1"]


def test_is_scanned():
    assert ap.is_scanned(100, 5)
    assert not ap.is_scanned(5000, 5)
    assert ap.is_scanned(0, 0)


def test_clean_ligatures_and_hyphenation():
    assert ap.clean("ﬁrst exper- iment") == "first experiment"


def test_demo_server_blocked_by_default():
    with pytest.raises(ap.ArticleParseError) as exc:
        ap.grobid_parse(b"x", grobid_url="https://kermitt2-grobid.hf.space")
    assert exc.value.code == "GROBID_DEMO_BLOCKED"


def test_verify_flags_fabricated_evidence_and_values():
    src = "Male Wistar rats received 10 mg/kg i.p. daily."
    ok = ap.verify(
        {"value": "10 mg/kg", "evidence": "received 10 mg/kg i.p.", "status": "found"},
        src,
    )
    assert ok["status"] == "found"
    fake = ap.verify(
        {"value": "5 mg/kg", "evidence": "completely unrelated sentence here", "status": "found"},
        src,
    )
    assert fake["status"] == "unverified"
    wrong = ap.verify(
        {"value": "20 mg/kg", "evidence": "received 10 mg/kg i.p.", "status": "found"},
        src,
    )
    assert wrong["status"] == "value_not_in_evidence"


def test_merge_pass1_wins_and_conflicts_flagged():
    a = {"value": "10 mg/kg", "status": "found"}
    b = {"value": "20 mg/kg", "status": "found"}
    assert ap.merge_field_results(a, None)["pass"] == "pass1"
    merged = ap.merge_field_results(a, b)
    assert merged["status"] == "conflict" and merged["alternatives"] == ["20 mg/kg"]
    assert ap.merge_field_results({"status": "not_found"}, b)["pass"] == "pass2"


def test_retrieve_ranks_relevant_paragraph():
    pytest.importorskip("rank_bm25")
    paras = ["we thank the funders", "animals received a dose of 5 mg/kg administered daily"]
    assert ap.retrieve(paras, "dose", k=1) == [paras[1]]


def test_pass1_chunks_respect_budget():
    art = ap.ParsedArticle(["a" * 400, "b" * 400], [], ["c" * 400], "")
    assert len(art.pass1_chunks(max_tokens=150)) == 3


def test_verify_evidence_on_extraction():
    from app.models.protocol import RawExtraction
    from app.services.extraction import verify_evidence

    src = "Male Wistar rats  received 10 mg/kg i.p.\ndaily for 14 days."
    raw = RawExtraction(
        study_type="x",
        species="rat",
        species_evidence="Male Wistar rats received 10 mg/kg i.p.",
        guideline_ref="TG 420",
        guideline_ref_evidence="OECD guideline fabricated by the model entirely",
        regulatory=True,
    )
    checks = verify_evidence(raw, src)
    assert checks["species"].status == "verified"
    assert checks["guideline_ref"].status == "unverified"
    assert checks["regulatory"].status == "no_evidence"


def _blank_pdf(pages: int) -> bytes:
    from io import BytesIO

    from pypdf import PdfWriter

    writer = PdfWriter()
    for _ in range(pages):
        writer.add_blank_page(width=100, height=100)
    buf = BytesIO()
    writer.write(buf)
    return buf.getvalue()


def test_split_pdf_leaves_short_pdf_untouched():
    raw = _blank_pdf(5)
    assert ap.split_pdf(raw, max_pages=15) == [raw]


def test_split_pdf_chunks_long_pdf_without_losing_pages():
    from io import BytesIO

    from pypdf import PdfReader

    chunks = ap.split_pdf(_blank_pdf(38), max_pages=15)
    counts = [len(PdfReader(BytesIO(c)).pages) for c in chunks]
    assert counts == [15, 15, 8]


def test_split_pdf_unreadable_bytes_pass_through():
    assert ap.split_pdf(b"not a pdf") == [b"not a pdf"]


def test_parse_article_merges_chunks_and_keeps_methods_state(monkeypatch):
    from lxml import etree

    def tei(body: str, abstract: str = "") -> object:
        ns = "http://www.tei-c.org/ns/1.0"
        return etree.fromstring(
            f'<TEI xmlns="{ns}"><teiHeader><profileDesc><abstract>{abstract}'
            f"</abstract></profileDesc></teiHeader><text><body>{body}</body></text></TEI>"
        )

    parts = iter(
        [
            tei("<div><head>Introduction</head><p>i</p></div>"
                "<div><head>Methods</head><p>m1</p></div>", "abs"),
            tei("<div><head>Dosing</head><p>m2</p></div>"
                "<div><head>Results</head><p>r1</p></div>"),
        ]
    )
    monkeypatch.setattr(ap, "split_pdf", lambda raw: [b"a", b"b"])
    monkeypatch.setattr(ap, "grobid_parse", lambda *a, **k: next(parts))
    article = ap.parse_article(b"x", grobid_url="https://example.invalid")
    assert article.methods == ["[Methods] m1", "[Dosing] m2"]
    assert article.abstract == "abs"


def test_split_methods_trailing_methods_without_parent_heading():
    # Nature-style layout: Methods subsections after Discussion, parent heading lost.
    sections = [
        ("Introduction", ["i"]),
        ("Results", ["r1"]),
        ("Discussion", ["d1"]),
        ("Online content", ["boilerplate"]),
        ("Mice", ["m1"]),
        ("Statistics", ["m2"]),
        ("Extended Data Fig. 1 | legend", ["x"]),
    ]
    methods, other = ap.split_methods(sections)
    assert methods == ["[Mice] m1", "[Statistics] m2"]
    assert "[Discussion] d1" in other and "[Online content] boilerplate" in other


def test_split_methods_between_introduction_and_results():
    sections = [
        ("INTRODUCTION", ["i"]),
        ("Constructs", ["m1"]),
        ("Cell culture studies", ["m2"]),
        ("RESULTS", []),
        ("KCTD17 levels rise", ["r1"]),
        ("DISCUSSION", ["d"]),
    ]
    methods, other = ap.split_methods(sections)
    assert methods == ["[Constructs] m1", "[Cell culture studies] m2"]
    assert "[KCTD17 levels rise] r1" in other


def test_split_methods_fallback_not_used_when_heading_found():
    sections = [
        ("Introduction", ["i"]),
        ("Methods", ["m1"]),
        ("Results", ["r1"]),
        ("Discussion", ["d1"]),
        ("Supplementary notes", ["s"]),
    ]
    methods, _ = ap.split_methods(sections)
    assert methods == ["[Methods] m1"]


def test_split_methods_no_methods_anywhere():
    methods, other = ap.split_methods([("Introduction", ["i"]), ("Results", ["r"])])
    assert methods == [] and len(other) == 2
