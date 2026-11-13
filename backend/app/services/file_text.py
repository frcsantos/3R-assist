"""Extract plain text from uploaded .txt / .html / .pdf documents."""

from __future__ import annotations

import re
from io import BytesIO

from app.services.url_text import MAX_EXTRACTED_CHARS, html_to_text

MAX_UPLOAD_BYTES = 15 * 1024 * 1024

_ALLOWED_EXTENSIONS = frozenset({".txt", ".html", ".htm", ".pdf"})
_ALLOWED_CONTENT_TYPES = frozenset(
    {
        "text/plain",
        "text/html",
        "application/pdf",
        "application/octet-stream",
    }
)


class FileTextError(Exception):
    def __init__(self, code: str, message: str) -> None:
        super().__init__(message)
        self.code = code
        self.message = message


def _extension(filename: str | None) -> str:
    name = (filename or "").strip().lower()
    if "." not in name:
        return ""
    return "." + name.rsplit(".", 1)[-1]


def _decode_text(raw: bytes) -> str:
    for encoding in ("utf-8", "utf-8-sig", "latin-1"):
        try:
            return raw.decode(encoding)
        except UnicodeDecodeError:
            continue
    return raw.decode("utf-8", errors="replace")


_PAGE_NUMBER_RE = re.compile(
    r"^\s*(?:page|p[áa]gina|p\.)?\s*\d+(?:\s*(?:of|de|/)\s*\d+)?\s*$", re.IGNORECASE
)
_REFERENCES_HEADING_RE = re.compile(
    r"^\s*(?:\d+[.)]?\s*)?(?:references|bibliography|literature cited|"
    r"refer[êe]ncias(?: bibliogr[áa]ficas)?|bibliografia)\s*:?\s*$",
    re.IGNORECASE,
)
_REPEAT_LINE_MAX_LEN = 100


def _line_key(line: str) -> str:
    """Normalise a line so headers differing only in page number compare equal."""
    return re.sub(r"\d+", "#", line.strip().lower())


def clean_pdf_pages(pages: list[str]) -> str:
    """Join PDF page texts, dropping noise that only inflates the prompt.

    Removes running headers/footers (short lines repeated across pages), bare page
    numbers and the reference list; rejoins words hyphenated across line breaks.
    """
    if len(pages) >= 3:
        counts: dict[str, int] = {}
        for page in pages:
            for key in {
                _line_key(line)
                for line in page.splitlines()
                if line.strip() and len(line.strip()) <= _REPEAT_LINE_MAX_LEN
            }:
                counts[key] = counts.get(key, 0) + 1
        threshold = max(3, int(len(pages) * 0.4))
        repeated = {key for key, n in counts.items() if n >= threshold}
    else:
        repeated = set()

    kept_pages: list[str] = []
    for page in pages:
        lines = [
            line
            for line in page.splitlines()
            if not _PAGE_NUMBER_RE.match(line)
            and _line_key(line) not in repeated
        ]
        kept_pages.append("\n".join(lines).strip())

    text = "\n\n".join(page for page in kept_pages if page)
    text = re.sub(r"(\w)-\n(\w)", r"\1\2", text)

    # Drop the reference list, but only if it starts after the first third of the
    # document (avoids cutting everything on a "References" line in a table of contents).
    lines = text.split("\n")
    offset = 0
    for index, line in enumerate(lines):
        if _REFERENCES_HEADING_RE.match(line) and offset > len(text) / 3:
            text = "\n".join(lines[:index])
            break
        offset += len(line) + 1

    text = re.sub(r"[ \t]+", " ", text)
    return re.sub(r"\n{3,}", "\n\n", text).strip()


def _truncate_at_boundary(text: str, limit: int) -> str:
    if len(text) <= limit:
        return text
    cut = text[:limit]
    boundary = cut.rfind("\n\n")
    if boundary < limit * 0.8:
        boundary = cut.rfind("\n")
    if boundary < limit * 0.8:
        return cut
    return cut[:boundary].rstrip()


def _pdf_to_text(raw: bytes) -> str:
    try:
        from pypdf import PdfReader
    except ImportError as exc:
        raise FileTextError(
            "FILE_READ_FAILED",
            "PDF support is not installed on the server.",
        ) from exc

    try:
        reader = PdfReader(BytesIO(raw))
    except Exception as exc:
        raise FileTextError(
            "FILE_READ_FAILED",
            "Could not read the PDF file.",
        ) from exc

    pages: list[str] = []
    for page in reader.pages:
        try:
            page_text = page.extract_text() or ""
        except Exception:
            page_text = ""
        cleaned = page_text.strip()
        if cleaned:
            pages.append(cleaned)

    text = clean_pdf_pages(pages)
    if len(text) < 20:
        raise FileTextError(
            "FILE_NO_TEXT",
            "Could not extract enough text from the PDF.",
        )
    return text


def extract_text_from_upload(
    *,
    filename: str | None,
    content_type: str | None,
    raw: bytes,
) -> str:
    if not raw:
        raise FileTextError("FILE_READ_FAILED", "The uploaded file is empty.")
    if len(raw) > MAX_UPLOAD_BYTES:
        raise FileTextError(
            "FILE_TOO_LARGE",
            "The uploaded file is too large.",
        )

    ext = _extension(filename)
    ctype = (content_type or "").split(";", 1)[0].strip().lower()

    if ext and ext not in _ALLOWED_EXTENSIONS:
        raise FileTextError(
            "FILE_TYPE_UNSUPPORTED",
            "Supported file types: PDF, HTML, TXT.",
        )
    if not ext and ctype and ctype not in _ALLOWED_CONTENT_TYPES:
        raise FileTextError(
            "FILE_TYPE_UNSUPPORTED",
            "Supported file types: PDF, HTML, TXT.",
        )

    kind = ext.lstrip(".")
    if not kind:
        if ctype == "application/pdf":
            kind = "pdf"
        elif ctype == "text/html":
            kind = "html"
        else:
            kind = "txt"

    if kind == "pdf":
        text = _pdf_to_text(raw)
    elif kind in {"html", "htm"}:
        text = html_to_text(_decode_text(raw))
        if len(text) < 20:
            raise FileTextError(
                "FILE_NO_TEXT",
                "Could not extract enough text from the HTML file.",
            )
    else:
        text = _decode_text(raw).strip()
        if len(text) < 20:
            raise FileTextError(
                "FILE_NO_TEXT",
                "Could not extract enough text from the file.",
            )

    return _truncate_at_boundary(text, MAX_EXTRACTED_CHARS)
