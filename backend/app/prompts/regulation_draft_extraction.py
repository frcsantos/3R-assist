"""Build prompts for extracting regulations-table draft fields from source text."""

REGULATION_DRAFT_EXTRACTION_PROMPT_TEMPLATE = """You are a scientific curator for a 3Rs alternative-methods database.

Extract structured draft fields for ONE method-regulatory-context / regulations
row from the text below. The output will pre-fill a curation form; prefer
precision over completeness.

STRICT EXTRACTION MODE: Extract only what is supported by the text.
Do not invent jurisdictions, statuses, bodies, dates, or citations that are not
clearly present. If a field is not supported, return null.

── CONTROLLED VOCABULARIES ──────────────────────────────────────────────────
jurisdiction — prefer one of these localized pairs when supported:
  Brazil/Brasil, EU/UE, US/EUA, OECD/OCDE
  Return {"en-us":"...","pt-br":"..."}. If only one language is present, copy
  into both locales. Null if unclear.

regulatory_status — exactly one of:
  not_approved, approved, recommended, mandatory
  (or null if unclear)

── FIELD GUIDANCE ───────────────────────────────────────────────────────────
- regulatory_date: adoption / recognition / issuance date. Prefer ISO
  YYYY-MM-DD; year-only as YYYY-01-01 when only the year is known; else null.
- regulatory_endpoints: integer ids of recognized endpoints when the
  text names specific toxicological endpoints and those ids are known;
  otherwise null. Do not invent ids.
- endpoint_quote: verbatim supporting quotation from the text for the
  recognized endpoints; otherwise null. Do not paraphrase.
- regulatory_body: issuing body, localized {"en-us":"...","pt-br":"..."}.
  Examples: OECD/OCDE, CONCEA. Copy into both locales when only one language
  is present. Null if unclear.
- regulatory_citation: bibliographic citation / short reference, localized
  {"en-us":"...","pt-br":"..."}. Copy into both locales when only one language
  is present. Null if unclear.
- notes: free-text applicability limits or caveats when present; otherwise null.

── OUTPUT FORMAT ────────────────────────────────────────────────────────────
Return ONLY valid JSON. No preamble. No markdown. No explanation outside JSON.
Your first character must be `{`. Do not write reasoning before the JSON object.

Schema:
{
  "jurisdiction": {"en-us": "string", "pt-br": "string"} or null,
  "regulatory_status": "not_approved|approved|recommended|mandatory|null",
  "regulatory_date": "string or null",
  "regulatory_endpoints": [1, 2] or null,
  "endpoint_quote": "string or null",
  "regulatory_body": {"en-us": "string", "pt-br": "string"} or null,
  "regulatory_citation": {"en-us": "string", "pt-br": "string"} or null,
  "notes": "string or null"
}

── HINTS ────────────────────────────────────────────────────────────────────
Source URL (optional): {source_url}

── SOURCE TEXT ──────────────────────────────────────────────────────────────
Document text:
{document_text}
"""


def build_regulation_draft_extraction_prompt(
    document_text: str,
    *,
    source_url: str | None = None,
) -> str:
    return (
        REGULATION_DRAFT_EXTRACTION_PROMPT_TEMPLATE.replace(
            "{document_text}",
            document_text.strip(),
        ).replace("{source_url}", (source_url or "none").strip() or "none")
    )
