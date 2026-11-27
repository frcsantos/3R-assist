"""Article PDF -> Methods text pipeline (see docs/protocol-extraction-pipeline.md).

Stages implemented here: GROBID parse, section split, cleaning, scanned-PDF
guard, BM25 retrieval for gap-filling, and evidence verification.
The LLM passes live in the extraction service; this module is LLM-free.
"""

from __future__ import annotations

import re
import time
import unicodedata

import httpx

NS = {"tei": "http://www.tei-c.org/ns/1.0"}

METHOD_KEYS = (
    "method", "materials", "experimental", "procedure", "protocol",
    "study design", "animals", "subjects", "participants", "star",
)
STOP_KEYS = ("result", "discussion", "conclusion", "acknowledg", "reference")
_BACK_MATTER_RE = re.compile(
    r"acknowledg|reference|funding|author contri|competing|conflict|"
    r"data availability|code availability|extended data|supplementary|"
    r"reporting summary|online content|additional information",
    re.IGNORECASE,
)

# Public demo servers: testing with public papers only (confidentiality).
# Heuristic substrings; extend if the demo host changes.
PUBLIC_DEMO_MARKERS = ("kermitt2", "science-miner", "grobid.work")

MIN_CHARS_PER_PAGE = 200
GROBID_TIMEOUT = 180.0
# Long/heavy PDFs are sent to GROBID in page chunks (see split_pdf).
GROBID_MAX_PAGES = 15
GROBID_MAX_CHUNK_BYTES = 8 * 1024 * 1024

FIELD_QUERIES: dict[str, list[str]] = {
    "n_per_group": ["n =", "per group", "animals per", "subjects", "sample size"],
    "dose": ["mg/kg", "dose", "µg", "administered", "concentration"],
    "duration": ["days", "weeks", "for", "period", "treatment lasted"],
    "route": ["intraperitoneal", "oral", "gavage", "intravenous", "subcutaneous", "i.p.", "i.v."],
    "species": ["rats", "mice", "species", "strain", "zebrafish"],
    "sex": ["male", "female", "sex"],
}


class ArticleParseError(Exception):
    def __init__(self, code: str, message: str) -> None:
        super().__init__(message)
        self.code = code


# --------------------------------------------------------------------------
# Cleaning and guards
# --------------------------------------------------------------------------

def clean(text: str) -> str:
    text = unicodedata.normalize("NFKC", text)
    text = re.sub(r"(\w)-\s+(\w)", r"\1\2", text)
    return re.sub(r"\s+", " ", text).strip()


def is_scanned(total_chars: int, page_count: int) -> bool:
    """True when extracted text density suggests a scanned/broken PDF."""
    if page_count <= 0:
        return True
    return total_chars / page_count < MIN_CHARS_PER_PAGE


def estimate_tokens(text: str) -> int:
    return len(text) // 4


# --------------------------------------------------------------------------
# GROBID
# --------------------------------------------------------------------------

def grobid_parse(
    raw: bytes,
    *,
    grobid_url: str,
    hf_token: str | None = None,
    timeout: float = GROBID_TIMEOUT,
    retries: int = 1,
    allow_public_demo: bool = False,
):
    """POST the PDF to GROBID and return the TEI root element.

    One retry with backoff covers HF Space cold starts.
    """
    from lxml import etree

    if allow_public_demo is False and any(
        marker in grobid_url.lower() for marker in PUBLIC_DEMO_MARKERS
    ):
        raise ArticleParseError(
            "GROBID_DEMO_BLOCKED",
            "GROBID_URL points at a public demo server. Use our own "
            "Hugging Face Space (private) for real PDFs.",
        )
    headers = {"Authorization": f"Bearer {hf_token}"} if hf_token else {}
    url = f"{grobid_url.rstrip('/')}/api/processFulltextDocument"
    last: Exception | None = None
    for attempt in range(retries + 1):
        try:
            resp = httpx.post(
                url,
                files={"input": ("article.pdf", raw, "application/pdf")},
                data={"consolidateHeader": "0", "consolidateCitations": "0"},
                headers=headers,
                timeout=timeout,
            )
            resp.raise_for_status()
            return etree.fromstring(resp.content)
        except (httpx.HTTPError, etree.XMLSyntaxError) as exc:
            last = exc
            if attempt < retries:
                time.sleep(5 * (attempt + 1))
    raise ArticleParseError("GROBID_FAILED", f"GROBID request failed: {last}")


def _text(el) -> str:
    return re.sub(r"\s+", " ", "".join(el.itertext())).strip()


def get_sections(tei) -> list[tuple[str, list[str]]]:
    out: list[tuple[str, list[str]]] = []
    for div in tei.iterfind(".//tei:body/tei:div", NS):
        head = div.findtext("tei:head", default="", namespaces=NS).strip()
        paras = [_text(p) for p in div.iterfind("tei:p", NS)]
        out.append((head, [p for p in paras if p]))
    return out


def get_abstract(tei) -> str:
    el = tei.find(".//tei:profileDesc/tei:abstract", NS)
    return _text(el) if el is not None else ""


def get_legends_and_tables(tei) -> list[str]:
    items: list[str] = []
    for fig in tei.iterfind(".//tei:figure", NS):
        head = fig.findtext("tei:head", default="", namespaces=NS) or ""
        desc = fig.find("tei:figDesc", NS)
        table = fig.find("tei:table", NS)
        parts = [head]
        if desc is not None:
            parts.append(_text(desc))
        if table is not None:
            parts.append(_text(table))
        txt = " ".join(p for p in parts if p).strip()
        if txt:
            items.append(txt)
    return items


def split_methods(
    sections: list[tuple[str, list[str]]],
) -> tuple[list[str], list[str]]:
    """Return (methods_paragraphs, other_paragraphs).

    Methods subsections often arrive as separate top-level divs, so we stay
    "inside" until a stop heading.
    """
    methods: list[str] = []
    other: list[str] = []
    inside = False
    for head, paras in sections:
        h = head.lower()
        if any(k in h for k in METHOD_KEYS):
            inside = True
        elif inside and any(k in h for k in STOP_KEYS):
            inside = False
        target = methods if inside else other
        target.extend(f"[{head}] {p}" if head else p for p in paras)
    if not methods:
        return _positional_methods(sections)
    return methods, other


def _is_stop(head: str) -> bool:
    return any(k in head.lower() for k in STOP_KEYS)


def _positional_methods(
    sections: list[tuple[str, list[str]]],
) -> tuple[list[str], list[str]]:
    """Fallback when no heading names a Methods section.

    GROBID often drops the parent "Methods" heading and returns only its
    subsections ("Mice", "Statistics"...), which match no METHOD_KEYS. Use the
    layout instead:
      * Methods at the end: everything after the last Results/Discussion/
        Conclusions heading, minus back-matter (acknowledgements, funding...).
      * Methods before Results: sections between the Introduction and the
        first Results heading.
    Returns ([], all) when neither layout is found.
    """
    def fmt(head: str, paras: list[str]) -> list[str]:
        return [f"[{head}] {p}" if head else p for p in paras]

    stop_idx = [i for i, (h, _) in enumerate(sections) if _is_stop(h)]
    chosen: set[int] = set()

    if stop_idx:
        last = stop_idx[-1]
        tail = [
            i
            for i in range(last + 1, len(sections))
            if not _BACK_MATTER_RE.search(sections[i][0])
        ]
        if any(sections[i][1] for i in tail):
            chosen = set(tail)

    if not chosen:
        first_results = next(
            (i for i, (h, _) in enumerate(sections) if "result" in h.lower()), None
        )
        intro = next(
            (i for i, (h, _) in enumerate(sections) if "introduction" in h.lower()),
            None,
        )
        if first_results is not None and intro is not None and first_results > intro + 1:
            between = range(intro + 1, first_results)
            if any(sections[i][1] for i in between):
                chosen = set(between)

    methods: list[str] = []
    other: list[str] = []
    for i, (head, paras) in enumerate(sections):
        (methods if i in chosen else other).extend(fmt(head, paras))
    return methods, other


class ParsedArticle:
    def __init__(
        self,
        methods: list[str],
        other: list[str],
        legends: list[str],
        abstract: str,
    ) -> None:
        self.methods = methods
        self.other = other
        self.legends = legends
        self.abstract = abstract

    @property
    def has_methods(self) -> bool:
        return bool(self.methods)

    def pass1_chunks(self, max_tokens: int = 5000) -> list[str]:
        """Methods + legends/tables split into chunks within the token budget."""
        paragraphs = [clean(p) for p in self.methods + self.legends]
        chunks: list[str] = []
        current: list[str] = []
        size = 0
        for p in paragraphs:
            t = estimate_tokens(p)
            if current and size + t > max_tokens:
                chunks.append("\n\n".join(current))
                current, size = [], 0
            current.append(p)
            size += t
        if current:
            chunks.append("\n\n".join(current))
        return chunks

    def retrieval_pool(self) -> list[str]:
        pool = [clean(p) for p in self.other]
        if self.abstract:
            pool.insert(0, clean(self.abstract))
        return pool


def split_pdf(
    raw: bytes,
    *,
    max_pages: int = GROBID_MAX_PAGES,
    max_bytes: int = GROBID_MAX_CHUNK_BYTES,
) -> list[bytes]:
    """Split a long or heavy PDF into consecutive page chunks for GROBID.

    Returns [raw] unchanged when it is already within both limits (or cannot be
    read, so GROBID reports the real error). Chunks never overlap; a section
    that straddles a boundary loses its heading in the second chunk.
    """
    from io import BytesIO

    from pypdf import PdfReader, PdfWriter

    try:
        reader = PdfReader(BytesIO(raw))
        total = len(reader.pages)
    except Exception:
        return [raw]
    if total <= max_pages and len(raw) <= max_bytes:
        return [raw]

    per_chunk = max_pages
    if len(raw) > max_bytes:
        # Size is dominated by page images; scale chunk length by bytes/page.
        per_chunk = min(per_chunk, max(1, int(total * max_bytes / len(raw) * 0.8)))

    chunks: list[bytes] = []
    for start in range(0, total, per_chunk):
        writer = PdfWriter()
        for index in range(start, min(start + per_chunk, total)):
            writer.add_page(reader.pages[index])
        buf = BytesIO()
        writer.write(buf)
        chunks.append(buf.getvalue())
    return chunks


def parse_article(
    raw: bytes,
    *,
    grobid_url: str,
    hf_token: str | None = None,
    allow_public_demo: bool = False,
) -> ParsedArticle:
    sections: list[tuple[str, list[str]]] = []
    legends: list[str] = []
    abstract = ""
    for chunk in split_pdf(raw):
        tei = grobid_parse(
            chunk,
            grobid_url=grobid_url,
            hf_token=hf_token,
            allow_public_demo=allow_public_demo,
        )
        sections.extend(get_sections(tei))
        legends.extend(get_legends_and_tables(tei))
        abstract = abstract or get_abstract(tei)
    # Sections are merged before the Methods split so "inside Methods" state
    # carries across chunk boundaries.
    methods, other = split_methods(sections)
    return ParsedArticle(
        methods=methods,
        other=other,
        legends=legends,
        abstract=abstract,
    )


# --------------------------------------------------------------------------
# Pass 2 retrieval
# --------------------------------------------------------------------------

def retrieve(paragraphs: list[str], field: str, k: int = 4) -> list[str]:
    from rank_bm25 import BM25Plus

    if not paragraphs or field not in FIELD_QUERIES:
        return []
    bm25 = BM25Plus([p.lower().split() for p in paragraphs])
    query = " ".join(FIELD_QUERIES[field]).lower().split()
    scores = bm25.get_scores(query)
    ranked = sorted(range(len(paragraphs)), key=lambda i: scores[i], reverse=True)
    return [paragraphs[i] for i in ranked[:k] if scores[i] > 0]


def retrieve_for_fields(
    paragraphs: list[str], fields: list[str], k: int = 4
) -> list[str]:
    """Deduplicated union of top-k paragraphs across the missing fields."""
    seen: dict[str, None] = {}
    for field in fields:
        for p in retrieve(paragraphs, field, k):
            seen.setdefault(p)
    return list(seen)


# --------------------------------------------------------------------------
# Verification and merging
# --------------------------------------------------------------------------

def value_in_evidence(value: object, evidence: str) -> bool:
    nums = re.findall(r"\d+(?:[.,]\d+)?", str(value))
    return all(n in evidence for n in nums)


def verify(field_result: dict, source_text: str, threshold: int = 90) -> dict:
    """Fuzzy-check the evidence quote against the source; flag mismatches."""
    from rapidfuzz import fuzz

    ev = field_result.get("evidence")
    if field_result.get("status") != "found" or not ev:
        return field_result
    score = fuzz.partial_ratio(ev.lower(), source_text.lower())
    field_result["evidence_score"] = score
    if score < threshold:
        field_result["status"] = "unverified"
    elif field_result.get("value") and not value_in_evidence(
        field_result["value"], ev
    ):
        field_result["status"] = "value_not_in_evidence"
    return field_result


def merge_field_results(pass1: dict | None, pass2: dict | None) -> dict | None:
    """Pass 1 wins; two differing verified values become a conflict."""
    candidates = [
        (name, r)
        for name, r in (("pass1", pass1), ("pass2", pass2))
        if r and r.get("status") == "found"
    ]
    if not candidates:
        return pass1 or pass2
    first_name, first = candidates[0]
    first = {**first, "pass": first_name}
    if len(candidates) == 2:
        second = candidates[1][1]
        if str(second.get("value")).strip().lower() != str(first.get("value")).strip().lower():
            first["status"] = "conflict"
            first["alternatives"] = [second.get("value")]
    return first
