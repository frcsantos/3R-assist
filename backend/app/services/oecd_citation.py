"""Build standard OECD Test Guideline bibliographic citations from scraped text."""

from __future__ import annotations

import re

_MONTH = (
    r"January|February|March|April|May|June|July|"
    r"August|September|October|November|December"
)

_TEST_NO_RE = re.compile(
    r"Test\s+No\.?\s*(\d{3,4}[A-Za-z]?)\s*:\s*([^\n\r]+)",
    re.IGNORECASE,
)
_SERIES_RE = re.compile(
    r"OECD\s+Guidelines\s+for\s+the\s+Testing\s+of\s+Chemicals"
    r"(?:\s*,?\s*Section\s*(\d+))?",
    re.IGNORECASE,
)
_DATE_RE = re.compile(
    rf"\b(\d{{1,2}})\s*({_MONTH})\s*(\d{{4}})\b",
    re.IGNORECASE,
)


def _fix_title_spacing(title: str) -> str:
    cleaned = re.sub(r"\s+", " ", title).strip()
    cleaned = re.sub(r"\bReport\b.*$", "", cleaned, flags=re.IGNORECASE).strip()
    cleaned = re.sub(r"(?<=[a-z])(?=[A-Z])", " ", cleaned)
    cleaned = re.sub(r"(?<=[A-Za-z])(?=\d)", " ", cleaned)
    return re.sub(r"\s+", " ", cleaned).strip(" :-")


def _collapse_letter_spaced_line(line: str) -> str | None:
    stripped = line.strip()
    if not stripped:
        return None
    word_groups = re.split(r"\s{2,}", stripped)
    if len(word_groups) < 2:
        return None
    words: list[str] = []
    for group in word_groups:
        letters = group.split()
        if not letters or not all(len(tok) == 1 and tok.isalpha() for tok in letters):
            return None
        words.append("".join(letters))
    if len(words) < 2:
        return None
    return " ".join(words)


def _find_spaced_subtitle(text: str, *, after: int = 0) -> str | None:
    head = text[after : after + 1500]
    for line in head.splitlines():
        collapsed = _collapse_letter_spaced_line(line)
        if collapsed and len(collapsed) >= 8:
            return collapsed
    return None


def _normalize_test_number(raw: str) -> str:
    raw = raw.strip()
    if raw and raw[-1].isalpha():
        return raw[:-1] + raw[-1].upper()
    return raw


def build_oecd_tg_citation(text: str) -> str | None:
    """Return OECD Publishing-style TG citation when the text supports it.

    Example:
    OECD (2026), Test No. 429: Skin Sensitisation: Local Lymph Node Assay,
    OECD Guidelines for the Testing of Chemicals, Section 4, OECD Publishing, Paris,
    """
    if not text or not text.strip():
        return None

    series = _SERIES_RE.search(text)
    test = _TEST_NO_RE.search(text)
    if test is None or series is None:
        return None

    number = _normalize_test_number(test.group(1))
    title = _fix_title_spacing(test.group(2))
    if not title:
        return None

    subtitle = _find_spaced_subtitle(text, after=test.end())
    title_part = title
    if subtitle and subtitle.casefold() not in title.casefold():
        title_part = f"{title}: {subtitle}"

    date = _DATE_RE.search(text)
    year = date.group(3) if date else None
    if year is None:
        year_match = re.search(r"\b(20\d{2})\b", text)
        year = year_match.group(1) if year_match else None
    if year is None:
        return None

    section = series.group(1)
    section_part = f", Section {section}" if section else ""

    return (
        f"OECD ({year}), Test No. {number}: {title_part}, "
        f"OECD Guidelines for the Testing of Chemicals{section_part}, "
        f"OECD Publishing, Paris,"
    )


def prefer_oecd_tg_citation(existing: str | None, text: str | None) -> str | None:
    """Prefer a constructed OECD TG citation over a weaker scraped title."""
    if not text:
        return existing
    built = build_oecd_tg_citation(text)
    if built is None:
        return existing
    if not existing:
        return built
    if existing.strip().startswith("OECD (") and "OECD Publishing" in existing:
        return existing
    return built
