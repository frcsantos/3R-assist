"""Build prompts for extracting documents-table draft fields from source text."""

DOCUMENT_DRAFT_EXTRACTION_PROMPT_TEMPLATE = """You are a scientific curator for a 3Rs alternative-methods database.

Extract structured draft fields for ONE source document catalogue entry from the
text below. The output will pre-fill a curation form; prefer precision over
completeness.

STRICT EXTRACTION MODE: Extract only what is supported by the text.
Do not invent titles, dates, URLs, or categories that are not clearly present.
If a field is not supported, return null.

── CONTROLLED VOCABULARY ────────────────────────────────────────────────────
categories — one or more of:
  method_protocol, guideline, regulation, other
  Use method_protocol for method/TG/protocol documents.
  Use guideline for guidance documents that are not binding regulations.
  Use regulation for laws, resolutions, decrees, or binding regulatory texts.
  Use other when none of the above fits.
  Include every clearly supported kind (e.g. a regulatory method protocol may
  be ["method_protocol","regulation"]). Prefer a non-empty array.
  If a preferred category hint is provided below, include it unless the text
  clearly indicates different categories.

── FIELD GUIDANCE ───────────────────────────────────────────────────────────
- slug: URL-safe lowercase identifier derived from the citation/title
  (e.g. "oecd-tg439", "concea-rn-18-2014"). Max 80 characters.
- date: publication / adoption / issuance date. Prefer ISO YYYY-MM-DD when
  day/month/year are clear; otherwise year-only as YYYY-01-01 when only the
  year is known; otherwise null.
- url: canonical document URL only if explicitly present in the text.
  If a source URL hint is provided below and the text has no other URL, use
  the hint. Otherwise null.
- categories: see controlled vocabulary above.
- institution: localized issuing / responsible body
  {"en-us": "...", "pt-br": "..."}. Agency, ministry, council, or publisher
  named in the text (e.g. OECD, CONCEA). Null if unsupported.
- doc_citation: localized citation/title {"en-us": "...", "pt-br": "..."}.
  Prefer a formal bibliographic citation over a short page title.
  For OECD Test Guidelines, use this form when the text supports it:
  "OECD (YYYY), Test No. NNN: Title: Subtitle, OECD Guidelines for the
  Testing of Chemicals, Section N, OECD Publishing, Paris,"
  Example: "OECD (2026), Test No. 429: Skin Sensitisation: Local Lymph
  Node Assay, OECD Guidelines for the Testing of Chemicals, Section 4,
  OECD Publishing, Paris,"
  Repair missing spaces in scraped titles and expand letter-spaced
  subtitles when present. If only one language is present, copy the same
  string into both locales.
- description: localized short summary {"en-us": "...", "pt-br": "..."}.
  Each locale string must be at most 300 characters. Summarize what the
  document is (purpose/scope), not a full abstract. Null if unsupported.

── OUTPUT FORMAT ────────────────────────────────────────────────────────────
Return ONLY valid JSON. No preamble. No markdown. No explanation outside JSON.
Your first character must be `{`. Do not write reasoning before the JSON object.

Schema:
{
  "slug": "string or null",
  "date": "string or null",
  "url": "string or null",
  "categories": ["method_protocol|guideline|regulation|other"] or null,
  "institution": {"en-us": "string", "pt-br": "string"} or null,
  "doc_citation": {"en-us": "string", "pt-br": "string"} or null,
  "description": {"en-us": "string", "pt-br": "string"} or null
}

── HINTS ────────────────────────────────────────────────────────────────────
Detected source language: {source_language}. Put the native title/citation
in that locale; still fill both locales (copy when only one language is present).
Preferred category (optional): {category_hint}
Source URL (optional): {source_url}

── SOURCE TEXT ──────────────────────────────────────────────────────────────
Document text:
{document_text}
"""


def build_document_draft_extraction_prompt(
    document_text: str,
    *,
    category_hint: str | None = None,
    source_url: str | None = None,
    source_language: str = "English",
) -> str:
    return (
        DOCUMENT_DRAFT_EXTRACTION_PROMPT_TEMPLATE.replace(
            "{document_text}",
            document_text.strip(),
        )
        .replace("{category_hint}", (category_hint or "none").strip() or "none")
        .replace("{source_url}", (source_url or "none").strip() or "none")
        .replace("{source_language}", source_language)
    )
