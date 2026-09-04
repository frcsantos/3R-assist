"""Fetch a public HTTP(S) URL and extract readable text from the HTML page."""

from __future__ import annotations

import ipaddress
import re
import socket
from html.parser import HTMLParser
from urllib.parse import urlparse

import httpx

MAX_RESPONSE_BYTES = 5 * 1024 * 1024
MAX_EXTRACTED_CHARS = 50_000
FETCH_TIMEOUT_SECONDS = 30.0
MAX_REDIRECTS = 5

_BLOCKED_HOSTNAMES = frozenset(
    {
        "localhost",
        "metadata.google.internal",
        "metadata",
    }
)


class UrlTextError(Exception):
    def __init__(self, code: str, message: str) -> None:
        if code in {"INVALID_URL", "URL_FETCH_FAILED", "URL_NO_TEXT"}:
            message = _with_paste_hint(message)
        super().__init__(message)
        self.code = code
        self.message = message


PASTE_HINT = " Paste the page content instead."


def _with_paste_hint(message: str) -> str:
    if "paste" in message.lower() and "content" in message.lower():
        return message if message.endswith(".") else f"{message}."
    trimmed = message.rstrip(".")
    return f"{trimmed}.{PASTE_HINT}"


async def resolve_extraction_source(raw_text: str) -> tuple[str, str | None]:
    """Return `(text_for_prompt, source_url)`.

    When `raw_text` is a URL, fetch and extract page text. Otherwise return
    the text unchanged with `source_url=None`.
    """
    fetch_url = parse_as_fetch_url(raw_text)
    if fetch_url is not None:
        return await fetch_url_text(fetch_url), fetch_url
    if raw_text.lower().startswith(("http://", "https://", "www.")):
        raise UrlTextError("INVALID_URL", "Invalid URL.")
    return raw_text, None


class _HTMLTextExtractor(HTMLParser):
    _SKIP_TAGS = frozenset(
        {"script", "style", "noscript", "svg", "iframe", "template"}
    )

    def __init__(self) -> None:
        super().__init__(convert_charrefs=True)
        self._parts: list[str] = []
        self._skip_depth = 0
        self.title: str | None = None
        self._in_title = False

    def handle_starttag(self, tag: str, attrs: list[tuple[str, str | None]]) -> None:
        lower = tag.lower()
        if lower in self._SKIP_TAGS:
            self._skip_depth += 1
            return
        if lower == "title" and self._skip_depth == 0:
            self._in_title = True

    def handle_endtag(self, tag: str) -> None:
        lower = tag.lower()
        if lower in self._SKIP_TAGS and self._skip_depth > 0:
            self._skip_depth -= 1
            return
        if lower == "title":
            self._in_title = False

    def handle_data(self, data: str) -> None:
        text = data.strip()
        if not text:
            return
        if self._in_title:
            self.title = text if not self.title else f"{self.title} {text}"
            return
        if self._skip_depth == 0:
            self._parts.append(text)


def parse_as_fetch_url(text: str) -> str | None:
    """Return a normalized http(s) URL if `text` is solely a URL, else None."""
    candidate = text.strip()
    if not candidate or any(ch.isspace() for ch in candidate):
        return None

    if re.match(r"^https?://", candidate, flags=re.IGNORECASE):
        url = candidate
    elif candidate.lower().startswith("www.") and "." in candidate[4:]:
        url = f"https://{candidate}"
    else:
        return None

    parsed = urlparse(url)
    if parsed.scheme not in {"http", "https"}:
        return None
    if not parsed.hostname:
        return None
    return url


def html_to_text(html: str) -> str:
    parser = _HTMLTextExtractor()
    parser.feed(html)
    parser.close()

    chunks: list[str] = []
    if parser.title:
        chunks.append(parser.title.strip())
    body = re.sub(r"[ \t]+", " ", "\n".join(parser._parts))
    body = re.sub(r"\n{3,}", "\n\n", body).strip()
    if body:
        chunks.append(body)
    return "\n\n".join(chunks).strip()


def _hostname_resolves_to_public_ip(hostname: str) -> bool:
    lowered = hostname.lower().rstrip(".")
    if lowered in _BLOCKED_HOSTNAMES or lowered.endswith(".localhost"):
        return False

    try:
        addr = ipaddress.ip_address(lowered)
    except ValueError:
        addr = None
    if addr is not None:
        return _is_public_ip(addr)

    try:
        infos = socket.getaddrinfo(hostname, None)
    except socket.gaierror as exc:
        raise UrlTextError(
            "URL_FETCH_FAILED",
            "Could not resolve the URL hostname.",
        ) from exc

    if not infos:
        raise UrlTextError(
            "URL_FETCH_FAILED",
            "Could not resolve the URL hostname.",
        )

    saw_public = False
    for info in infos:
        raw = info[4][0]
        try:
            ip = ipaddress.ip_address(raw)
        except ValueError:
            continue
        if not _is_public_ip(ip):
            return False
        saw_public = True
    return saw_public


def _is_public_ip(ip: ipaddress.IPv4Address | ipaddress.IPv6Address) -> bool:
    return not (
        ip.is_private
        or ip.is_loopback
        or ip.is_link_local
        or ip.is_multicast
        or ip.is_reserved
        or ip.is_unspecified
    )


def _assert_safe_url(url: str) -> None:
    parsed = urlparse(url)
    if parsed.scheme not in {"http", "https"}:
        raise UrlTextError("INVALID_URL", "Only http and https URLs are supported.")
    hostname = parsed.hostname
    if not hostname:
        raise UrlTextError("INVALID_URL", "Invalid URL.")
    if not _hostname_resolves_to_public_ip(hostname):
        raise UrlTextError(
            "INVALID_URL",
            "URL points to a disallowed or private network address.",
        )


async def fetch_url_text(url: str) -> str:
    """Fetch `url` and return extracted page text.

    Raises UrlTextError when the URL is invalid, blocked, fetch fails,
    or no usable text can be extracted.
    """
    if parse_as_fetch_url(url) is None:
        raise UrlTextError("INVALID_URL", "Invalid URL.")

    current = url
    _assert_safe_url(current)

    try:
        async with httpx.AsyncClient(
            follow_redirects=False,
            timeout=FETCH_TIMEOUT_SECONDS,
            headers={
                "User-Agent": "3R-Assist/1.0 (document extraction)",
                "Accept": "text/html,application/xhtml+xml;q=0.9,*/*;q=0.8",
            },
        ) as client:
            response: httpx.Response | None = None
            for _ in range(MAX_REDIRECTS + 1):
                response = await client.get(current)
                if response.is_redirect:
                    location = response.headers.get("location")
                    if not location:
                        raise UrlTextError(
                            "URL_FETCH_FAILED",
                            "Could not fetch the URL.",
                        )
                    current = str(response.url.join(location))
                    _assert_safe_url(current)
                    continue
                break
            else:
                raise UrlTextError(
                    "URL_FETCH_FAILED",
                    "Too many redirects while fetching the URL.",
                )
    except UrlTextError:
        raise
    except httpx.TimeoutException as exc:
        raise UrlTextError(
            "URL_FETCH_FAILED",
            "Timed out while fetching the URL.",
        ) from exc
    except httpx.HTTPError as exc:
        raise UrlTextError(
            "URL_FETCH_FAILED",
            "Could not fetch the URL.",
        ) from exc

    assert response is not None

    if response.status_code >= 400:
        raise UrlTextError(
            "URL_FETCH_FAILED",
            f"Could not fetch the URL (HTTP {response.status_code}).",
        )

    content_type = (response.headers.get("content-type") or "").lower()
    if "pdf" in content_type:
        raise UrlTextError(
            "URL_FETCH_FAILED",
            "PDF URLs are not supported; paste the document text instead.",
        )

    raw = response.content
    if len(raw) > MAX_RESPONSE_BYTES:
        raise UrlTextError(
            "URL_FETCH_FAILED",
            "The page is too large to fetch.",
        )

    charset = response.charset_encoding or "utf-8"
    try:
        html = raw.decode(charset, errors="replace")
    except LookupError:
        html = raw.decode("utf-8", errors="replace")

    if (
        "html" in content_type
        or "<html" in html[:1000].lower()
        or "<!doctype" in html[:200].lower()
    ):
        text = html_to_text(html)
    else:
        text = html.strip()

    text = re.sub(r"\n{3,}", "\n\n", text).strip()
    if len(text) < 20:
        raise UrlTextError(
            "URL_NO_TEXT",
            "Could not extract enough text from the page.",
        )

    if len(text) > MAX_EXTRACTED_CHARS:
        text = text[:MAX_EXTRACTED_CHARS]

    return text
