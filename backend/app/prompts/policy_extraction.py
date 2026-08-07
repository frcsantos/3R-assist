"""Build prompts for extracting approved/recognized methods from policy documents."""

POLICY_EXTRACTION_PROMPT_TEMPLATE = """You are a scientific regulatory assistant specializing in animal research
ethics, alternatives to animal testing (3Rs), and recognized test methods.

Extract structured information from the policy / guidance / regulation text below.

STRICT EXTRACTION MODE: Extract only what is explicitly stated in the text.
Do not invent methods, codes, institutions, titles, or dates that are not present.
If a field is not explicitly stated, return null (or an empty methods array).

── WHAT TO EXTRACT ──────────────────────────────────────────────────────────
1. methods — approved, recognized, accepted, validated, or otherwise endorsed
   test methods / guidelines / protocols named in the document.
   Each method must be a (code, name, purpose, status) object:
     - code: exactly ONE official identifier (e.g. "TG 439", "OECD TG 492",
       "ISO 10993-10", "RN 18/2014", article/annex reference). If no code is
       given, use a short abbreviation from the text or "n/a".
     - name: full method title or clear descriptive name as stated.
     - purpose: what the method is approved/recognized for (endpoint, use,
       or regulatory purpose), as stated or clearly implied by the surrounding
       text. If not stated, return null.
     - status: regulatory standing for this method in the document. Must be
       one of: "not_approved", "approved", "recommended", "mandatory".
       Map wording in the text (e.g. accepted/recognized/validated →
       "approved"; recommended/preferred → "recommended"; mandatory/required
       /obrigatório → "mandatory"; rejected/not accepted → "not_approved").
       If the standing is not clear, return null.
   ONE CODE PER METHOD: Never combine multiple method codes in a single
   entry. If the text groups codes together (e.g. "OECD TG 442A e 442B",
   "TG 442A and 442B", "OECD TG 439/442C", "ISO 10993-10 and 10993-23"),
   emit a separate methods[] item for each distinct code. Reuse the same
   name/purpose/status for each when the document applies them jointly.
   Include only methods that the document presents as approved/recognized/
   accepted/validated (or equivalent). Skip purely illustrative or rejected
   methods unless the document still lists them as recognized alternatives.

2. document_name — bibliographic citation of the document when possible.
   Prefer a formal citation over a short page title.
   For OECD Test Guidelines, use this form when the text supports it:
   "OECD (YYYY), Test No. NNN: Title: Subtitle, OECD Guidelines for the
   Testing of Chemicals, Section N, OECD Publishing, Paris,"
   Example: "OECD (2026), Test No. 429: Skin Sensitisation: Local Lymph
   Node Assay, OECD Guidelines for the Testing of Chemicals, Section 4,
   OECD Publishing, Paris,"
   Repair missing spaces in scraped titles (e.g. SkinSensitisation →
   Skin Sensitisation). Include a letter-spaced subtitle when present
   (e.g. "L o c a l  L y m p h  N o d e  A s s a y" → Local Lymph Node Assay).
   For other sources, use the official title/designation as written
   (e.g. "Resolução Normativa CONCEA nº 18/2014").
3. document_date — publication, adoption, or effective date.
   Prefer ISO date YYYY-MM-DD when day/month/year are clear; otherwise keep
   the date form as written (e.g. "September 2014", "2014").
4. responsible_institution — issuing / responsible body (agency, ministry,
   council, organization).
5. url — canonical document URL only if explicitly present in the text.
   If a source URL hint is provided below and the text has no other URL, use
   the hint. Otherwise null.
6. description — short summary of what the document is (purpose/scope), at most
   300 characters. Do not paste long excerpts. Null if unsupported.

── OUTPUT FORMAT ────────────────────────────────────────────────────────────
Return ONLY valid JSON. No preamble. No markdown. No explanation outside JSON.
Your first character must be `{`. Do not write reasoning before the JSON object.
The JSON must be complete: close every string with a double quote and close
every object and array with } and ].

Schema:
{
  "methods": [
    {
      "code": "string",
      "name": "string",
      "purpose": "string or null",
      "status": "not_approved|approved|recommended|mandatory|null"
    }
  ],
  "document_name": "string or null",
  "document_date": "string or null",
  "responsible_institution": "string or null",
  "url": "string or null",
  "description": "string or null"
}

── HINTS ────────────────────────────────────────────────────────────────────
Source URL (optional): {source_url}

── SOURCE TEXT ──────────────────────────────────────────────────────────────
Policy text:
{policy_text}
"""


def build_policy_extraction_prompt(
    policy_text: str,
    *,
    source_url: str | None = None,
) -> str:
    return (
        POLICY_EXTRACTION_PROMPT_TEMPLATE.replace(
            "{policy_text}",
            policy_text.strip(),
        ).replace(
            "{source_url}",
            (source_url or "none").strip() or "none",
        )
    )
