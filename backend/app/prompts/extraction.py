"""Build extraction prompts (P2 output contract)."""

P2_OUTPUT_SPEC = r'''── OUTPUT CONTRACT (P2) ────────────────────────────────────────────────────
Return only valid JSON, exactly one object with key "experiments". No code
fences, comments, preamble or additional keys. Every experiment has exactly
these fields. Use JSON null (never strings "unknown" or "null") for absent,
ambiguous or unsupported facts; include all fields even when null.

{
  "experiments": [
    {
      "study_type": null,
      "procedure_text": null,
      "procedure_text_evidence": null,
      "species": null,
      "species_evidence": null,
      "animal_counts": null,
      "animal_counts_evidence": null,
      "test_system": null,
      "test_system_evidence": null,
      "application": null,
      "application_evidence": null,
      "route": null,
      "route_evidence": null,
      "endpoints": [],
      "substances": [],
      "exposure": {
        "dose_levels": null,
        "dose_units": null,
        "frequency": null,
        "duration": null,
        "timing": null,
        "conditions": null
      },
      "exposure_evidence": null,
      "guideline_ref": null,
      "guideline_ref_evidence": null,
      "regulatory": null,
      "regulatory_evidence": null,
      "missing_or_ambiguous": [],
      "notes": null
    }
  ]
}

Field rules:
- study_type: short source-language description or null; keep the stated
  design and key stressor/exposure (e.g. "UV photocarcinogenesis", not just
  "carcinogenicity"); do not invent a regulatory or mechanistic classification
  from a substance alone.
- procedure_text: <=30 words in source language, or null.
- species: a DB-listed species slug or legacy marker "other", ONLY for a named
  organism; null ONLY for cell-culture/cell-line systems with no stated animal
  source (not "in_vitro"). Tissue or organs from a named animal (e.g. bovine
  eyes from a slaughterhouse) still count: use that species, with its evidence.
  If specific organism not in DB, use "other" and preserve its name in notes.
- animal_counts: null, or object with EXACT keys female/male/total/per_group,
  each integer or null; values must be explicitly stated, not calculated.
- test_system: nonempty array of values drawn from
  in_vivo/ex_vivo/in_vitro/in_chemico/in_silico/in_data, or null.
- application: active application slug or the documented DEFAULT_APPLICATION;
  if defaulted, application_evidence=null. This is coding, not a stated fact.
- route: nonempty array of active route slugs or null. Give a route ONLY if the
  text states how the substance reaches the test system; never infer one from
  the exposure type (e.g. UV or other radiation) or the tissue. Use an explicit
  surface contact route for isolated tissue if stated. Use "unspecified" (when
  available) only when administration is explicitly described without naming a
  route; if no chemical administration is reported, route is null. Do not force
  "not-applicable" for ex vivo.
- endpoints: array of objects, one per DISTINCT, explicitly assessed endpoint:
  {"slug": <active endpoint slug or null>,
   "label": <brief original-language endpoint name>,
   "role": "primary"|"secondary"|"unspecified",
   "evidence": <exact source quote> }.
  If explicitly measured but no catalog slug fits, slug=null and retain label.
  Zero endpoints => [] (NOT a guessed default). Mark primary only if the text
  clearly establishes it; multiple primary endpoints are permitted if explicit.
  Deduplicate synonymous measurements, but keep distinct biological outcomes.
- substances: array of objects:
  {"name": <verbatim substance/material name>,
   "role": "test"|"control"|"other"|"unknown",
   "evidence": <exact source quote>}.
  Use [] when none is stated. Do not infer administered compound from context.
- exposure: an object with 6 keys exactly. Report only source-stated details.
  dose_levels is an array of verbatim dose expressions or null;
  dose_units is a verbatim unit string or null;
  frequency, duration, timing, conditions are concise verbatim phrases or null.
  Never convert units or calculate cumulative doses. If multiple regimens
  belong to one experiment, preserve distinct regimens in notes and do not
  imply that a single dose or duration applies to all cohorts.
- exposure_evidence: exact short quote supporting the most important exposure
  specification, or null; unresolved conflicts go to missing_or_ambiguous.
- guideline_ref: OECD-style TG/GD identifier only if the procedure actually
  follows the guideline, not a background or comparison citation.
- regulatory: true if a named authority/guideline is cited, false only if
  explicitly described as non-regulatory, else null; does NOT itself establish
  compliance or recognition.
- missing_or_ambiguous: array of short FIELD NAMES relevant to matching whose
  facts are missing/contradictory. No hypothesized values.
- notes: <=2 concise source-language sentences for issues not represented.
- All *_evidence fields, including endpoint and substance evidence, must be
  EXACT, CONTIGUOUS quotes from the protocol text; maximum 15 words except
  procedure_text_evidence and regulatory_evidence (maximum 20). For species
  evidence maximum 5 words. If no quote supports a fact, make it null.

Experiment segmentation:
1. Split for explicitly different animal cohorts.
2. Split for materially distinct compounds, routes, or schedules with separate
   procedures; never split dose levels of the same compound alone.
3. Split independent labeled studies only when independently described.
4. Multiple assays/endpoints on the same animals are ONE experiment. Record
   all such endpoints; do not silently discard secondary measurements.
5. If the segmentation is genuinely unclear, use the least speculative split,
   flag uncertainty in missing_or_ambiguous, and describe it in notes.

Evidence/normalization:
- Extract source facts, then normalize with the active vocabularies. A clear
  synonym mapping (e.g., Sprague-Dawley -> rat) is allowed; an inferred
  experimental fact is not. Never create new slugs.
- SOURCE LANGUAGE: keep narrative and quoted evidence in {source_language}.
- Output every object and array fully closed and syntactically valid JSON.

Protocol description:
{protocol_text}'''

P2_PREAMBLE = '''You are a scientific assistant specializing in animal research ethics.
Extract experimental parameters from the protocol description without inventing facts.
Use explicit source statements or unambiguous vocabulary normalization only.
Preserve all distinct endpoints and details relevant to matching an animal
procedure to recognized alternative methods. Missing evidence is not evidence
of absence. Use only exact short quotations in evidence fields.

── CONTROLLED VOCABULARIES ──────────────────────────────────────────────────
{application_values}

{endpoint_values}

{route_values}

{species_values}
'''

P2_TEMPLATE = P2_PREAMBLE + '\n' + P2_OUTPUT_SPEC

# Backwards-compatible name.
EXTRACTION_PROMPT_TEMPLATE = P2_TEMPLATE


def _endpoint_values_block() -> str:
    from app.services.vocabulary import endpoint_prompt_lines

    lines = endpoint_prompt_lines()
    if not lines:
        return "Endpoint values: not available; use slug=null and keep the label."
    return (
        "Endpoint values (slug: name; indentation shows the hierarchy, deeper = more "
        "specific). Use a slug exactly as written:\n" + lines
    )


def _route_values_block() -> str:
    from app.services.vocabulary import route_prompt_lines

    return "Route values (active slugs; use exactly as written):\n" + route_prompt_lines()


def _species_values_block() -> str:
    from app.services.vocabulary import species_prompt_lines

    return (
        "Species values (active slugs; use exactly as written; null when only "
        "in-vitro/cell culture):\n" + species_prompt_lines()
    )


def build_extraction_prompt(protocol_text: str, *, source_language: str = "English") -> str:
    from app.services.vocabulary import DEFAULT_APPLICATION, application_prompt_lines

    template = (
        P2_TEMPLATE.replace(
            "{application_values}",
            f"Application values (slug: description; DEFAULT_APPLICATION = {DEFAULT_APPLICATION}):\n"
            + application_prompt_lines(),
        )
        .replace("{endpoint_values}", _endpoint_values_block())
        .replace("{route_values}", _route_values_block())
        .replace("{species_values}", _species_values_block())
    )
    return template.replace(
        "{protocol_text}",
        protocol_text.strip(),
    ).replace("{source_language}", source_language)
