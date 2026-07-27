"""Build prompts for extracting methods-table draft fields from a method protocol."""

METHOD_DRAFT_EXTRACTION_PROMPT_TEMPLATE = """You are a scientific curator for a 3Rs alternative-methods database.

Extract structured draft fields for ONE alternative / regulatory test method from the
protocol / guideline / method document text below. The output will pre-fill a
curation form; prefer precision over completeness.

STRICT EXTRACTION MODE: Extract only what is supported by the text.
Do not invent OECD references, endpoints, routes, or rationales that are not
clearly present. If a field is not supported, return null.

── CONTROLLED VOCABULARIES ──────────────────────────────────────────────────
endpoint_category — exactly one of:
  acute_toxicity, skin_irritation, skin_corrosion, ocular_irritation,
  skin_sensitisation, phototoxicity, genotoxicity, pyrogenicity, skin_absorption
  (or null if none fits)

routes_applicable — array of zero or more of:
  oral, intraperitoneal, intravenous, dermal, ocular, inhalation, in_vitro, other
  Use null (not []) when the document does not indicate applicable routes.

study_domain — exactly one of:
  general, pharma, cosmetics, chemical_safety

source_db — exactly one of when provenance is clear, else null:
  OECD_TG, ECVAM_DBALM, NICEATM, FARMACOPEIA_BR, TSAR
  Use OECD_TG when the document is (or clearly describes) an OECD Test Guideline.

oecd_ref — OECD Test Guideline or Guidance Document reference when present,
  normalized like "TG 439" or "GD 129". Null if not OECD.

── FIELD GUIDANCE ───────────────────────────────────────────────────────────
- slug: URL-safe lowercase identifier. If oecd_ref is a TG number N, prefer
  "oecd-tgN-short-descriptive-name" (e.g. "oecd-tg439-epiderm"). Always start
  OECD methods with "oecd-". Otherwise derive from the method name.
- name / description: localized objects {"en-us": "...", "pt-br": "..."}.
  If only one language is present, copy the same string into both locales.
- replacement_rationale / reduction_rationale / refinement_rationale: non-empty
  text only when the document clearly supports that 3R class; otherwise null.
- keywords: localized synonym arrays {"en-us": [...], "pt-br": [...]}; use []
  per locale when none.
- text_for_embedding: single English string combining identifier, name, and
  purpose/description suitable for semantic search.
- ncit_id: NCI Thesaurus ID only if explicitly stated; otherwise null.
- source_citation: bibliographic citation of the primary source when stated.
- active: always false (new curated entries start inactive).

── OUTPUT FORMAT ────────────────────────────────────────────────────────────
Return ONLY valid JSON. No preamble. No markdown. No explanation outside JSON.
Your first character must be `{`. Do not write reasoning before the JSON object.

Schema:
{
  "slug": "string or null",
  "name": {"en-us": "string", "pt-br": "string"} or null,
  "description": {"en-us": "string", "pt-br": "string"} or null,
  "endpoint_category": "string or null",
  "routes_applicable": ["string"] or null,
  "study_domain": "string or null",
  "oecd_ref": "string or null",
  "ncit_id": "string or null",
  "source_citation": "string or null",
  "source_db": "string or null",
  "replacement_rationale": "string or null",
  "reduction_rationale": "string or null",
  "refinement_rationale": "string or null",
  "keywords": {"en-us": ["string"], "pt-br": ["string"]},
  "text_for_embedding": "string or null",
  "active": false
}

── SOURCE TEXT ──────────────────────────────────────────────────────────────
Method protocol text:
{protocol_text}
"""


def build_method_draft_extraction_prompt(protocol_text: str) -> str:
    return METHOD_DRAFT_EXTRACTION_PROMPT_TEMPLATE.replace(
        "{protocol_text}",
        protocol_text.strip(),
    )
