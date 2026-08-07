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

    parts: list[str] = []
    for page in reader.pages:
        try:
            page_text = page.extract_text() or ""
        except Exception:
            page_text = ""
        cleaned = page_text.strip()
        if cleaned:
            parts.append(cleaned)

    text = re.sub(r"\n{3,}", "\n\n", "\n\n".join(parts)).strip()
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

    if len(text) > MAX_EXTRACTED_CHARS:
        text = text[:MAX_EXTRACTED_CHARS]
    return text
