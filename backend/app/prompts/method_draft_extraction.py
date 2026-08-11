"""Build prompts for extracting methods-table draft fields from a method protocol."""

METHOD_DRAFT_EXTRACTION_PROMPT_TEMPLATE = """You are a scientific curator for a 3Rs alternative-methods database.

Extract structured draft fields for ONE alternative / regulatory test method from the
protocol / guideline / method document text below. The output will pre-fill a
curation form; prefer precision over completeness.

STRICT EXTRACTION MODE: Extract only what is supported by the text.
Do not invent OECD references, endpoints, routes, animal-use classifications,
test systems, or rationales that are not clearly present. If a field is not
supported, return null.

── CONTROLLED VOCABULARIES ──────────────────────────────────────────────────
animal_use — exactly one of:
  none, animal_derived_material, slaughterhouse_byproduct,
  animals_killed_for_tissue, live_animals, mixed_or_variable
  (or null if unclear)
  Guidance:
  - none: no animals and no animal-derived materials
  - animal_derived_material: sera, antibodies, enzymes, or other products from
    animals without killing for this method's tissue harvest
  - slaughterhouse_byproduct: tissues/organs from animals already slaughtered
    for food or other primary purposes
  - animals_killed_for_tissue: animals killed specifically to obtain tissue for
    the method
  - live_animals: living animals used in the procedure
  - mixed_or_variable: more than one of the above clearly applies, or use varies

test_system — array of one or more of:
  in_silico, in_chemico, in_vitro, ex_vivo, in_vivo, hybrid, unclear
  Use null (not []) when the document does not indicate a test system.
  Include every clearly supported kind (e.g. ["in_chemico","in_vitro"]).
  Use hybrid when the document itself describes a hybrid/integrated approach;
  otherwise list the concrete systems. Use unclear only when a system is
  mentioned but cannot be classified.

endpoint_category — exactly one of:
  acute_toxicity, skin_irritation, skin_corrosion, ocular_irritation,
  skin_sensitisation, phototoxicity, genotoxicity, pyrogenicity, skin_absorption,
  reproductive_toxicity, endocrine_activity, photoreactivity, aquatic_toxicity,
  toxicokinetics, bacterial_endotoxin, rabies_diagnosis
  (or null if none fits)

routes_applicable — array of zero or more of:
  oral, intraperitoneal, intravenous, dermal, ocular, inhalation, other
  Use null (not []) when the document does not indicate applicable routes.
  Do not use in_vitro as a route; capture culture/assay modality in test_system.

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
- replacement_rationale / reduction_rationale / refinement_rationale: localized
  objects {"en-us": "...", "pt-br": "..."} only when the document clearly
  supports that 3R class; otherwise null. If only one language is present,
  copy the same string into both locales.
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
  "animal_use": "string or null",
  "test_system": ["string"] or null,
  "endpoint_category": "string or null",
  "routes_applicable": ["string"] or null,
  "study_domain": "string or null",
  "oecd_ref": "string or null",
  "ncit_id": "string or null",
  "source_citation": "string or null",
  "source_db": "string or null",
  "replacement_rationale": {"en-us": "string", "pt-br": "string"} or null,
  "reduction_rationale": {"en-us": "string", "pt-br": "string"} or null,
  "refinement_rationale": {"en-us": "string", "pt-br": "string"} or null,
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
