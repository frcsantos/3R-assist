"""Build extraction prompts from docs/parameter_model.md §9."""

EXTRACTION_PROMPT_TEMPLATE = """You are a scientific assistant specializing in animal research ethics.
Extract experimental parameters from the protocol description below.

STRICT EXTRACTION MODE: Extract only what is explicitly stated in the text.
Do not infer, assume, or use domain knowledge to fill gaps.
If a field is not explicitly stated, return null.
Use the notes field for any interpretation or likely inference.

CRITICAL: All _evidence fields must be short, exact quotes (maximum 15–20 words).
Do not quote entire paragraphs. Use the shortest phrase that supports the value.

── MULTI-EXPERIMENT SPLITTING ───────────────────────────────────────────────
Create a separate experiment object ONLY IF at least one of the following is true:
1. A different animal cohort is used (different group of animals — not the same
   animals measured at multiple timepoints or with multiple assays)
2. A materially different dosing regimen applies (different compound, different
   route, or different schedule — NOT different doses of the same compound)
3. A separate, explicitly-labelled study section describes an independent study
   (e.g. "Study 1", "Experiment 2", "Dose-range study")

Multiple assays on the same animals = one experiment object.
Multiple dose groups of the same compound = one experiment object.

── ROUTE SYNONYMS ───────────────────────────────────────────────────────────
CRITICAL: "route" describes how the test substance contacts the biological
system — NOT what type of biological system it is. For ex vivo preparations
(isolated corneas, skin discs, membrane models), choose the route that
describes substance-to-tissue contact, not the culture setup.

  ocular      ← instillation into eye, conjunctival, eye drop,
                  applied over cornea, applied to corneal surface,
                  applied to apex of cornea, ex vivo corneal application
                  (USE THIS for EVEIT, BCOP, ICE — even though they are
                  ex vivo systems, the substance contacts the corneal surface)

  cutaneous   ← topical, dermal, epicutaneous, skin application,
                  ex vivo skin disc, membrane model (Strat-M, Skin+)

  oral              ← p.o., gavage, gavagem, intragastric, intragástrico,
                       gastric tube, gastric intubation, dietary (mixed in feed)
  intraperitoneal   ← i.p.
  intravenous       ← i.v., endovenous
  intramuscular     ← i.m.
  subcutaneous      ← s.c., sub-cut
  intradermal       ← i.d.
  inhalation        ← aerosol, nose-only chamber, inhalation chamber,
                       whole-body exposure
  other             ← a known chemical administration route not listed above
  unspecified       ← a route may exist but is not reported
  not-applicable    ← no organism-level administration route applies
  multiple          ← more than one route, not recorded separately
  null              ← UV irradiation, radiation, physical exposure,
                       or cell-culture medium exposure without an oriented tissue
                       surface (assay modality belongs in test_system, not route)
                       (radiation is not a chemical administration route)

── APPLICATION VALUES ──────────────────────────────────────────────────────
{application_values}

── ENDPOINT VALUES ─────────────────────────────────────────────────────────
{endpoint_values}

── TEST SYSTEM VALUES ───────────────────────────────────────────────────────
How the protocol itself tests the substance (an array; most protocols have one):
  in_vivo     ← living animals dosed or exposed (including fish/amphibian embryos)
  ex_vivo     ← tissue or organs taken from animals and tested outside the body
                  (isolated corneas, skin discs, explants, perfused organs)
  in_vitro    ← cultured cells, reconstructed tissues, cell lines
  in_chemico  ← cell-free chemical or biochemical reactivity assays
  in_silico   ← computational models, QSAR, read-across
  in_data     ← analysis of existing data only (no new test)

── SPECIES SYNONYMS ─────────────────────────────────────────────────────────
  rat         ← Rattus norvegicus, Wistar, Sprague-Dawley, SD, F344, Fischer,
                  IGS, Crj:CD(SD), SKH (rat strain)
  mouse       ← Mus musculus, BALB/c, C57BL/6, SKH:HR1, hairless mouse
  rabbit      ← Oryctolagus cuniculus, New Zealand White
  guinea_pig  ← Cavia porcellus, cavie
  chicken     ← Gallus gallus
  zebrafish   ← Danio rerio
  in_vitro    ← cell culture, cell line, isolated cells
  other       ← any species not listed above (bovine, porcine, canine, etc.)

── OUTPUT FORMAT ────────────────────────────────────────────────────────────
Return ONLY valid JSON. No preamble. No markdown. No explanation outside JSON.
Your first character must be `{`. Do not write reasoning before the JSON object.
The JSON must be complete: close every string with a double quote and close
every object and array with } and ]. Never stop mid-field or mid-string.
Do NOT include a top-level "confidence" field. Confidence is per-field only —
each paired _confidence field reflects how directly that field's evidence
supports its value.

Per-field confidence scale:
  "high"   — evidence directly and explicitly states the value; no interpretation needed
  "medium" — evidence requires vocabulary mapping or mild inference
  "low"    — value extracted but evidence is tangential; user should verify
  null     — field is null; omit the confidence field

{
  "experiments": [
    {
      "study_type": "free-text description of the study type, e.g. 'prenatal
        developmental toxicity study' or 'in vivo genotoxicity battery'. Do not
        map to any controlled vocabulary here — describe what you see.",

      "route": array of controlled values (see synonyms above) or null,
      "route_evidence": "exact quote from text, MAX 15 WORDS" or null,
      "route_confidence": "high"|"medium"|"low" or null if route is null,

      "application": one of the slugs listed under "Application values" below,
      "application_evidence": "exact quote from text, MAX 15 WORDS" or null,
      "application_confidence": "high"|"medium"|"low",
      // Choose the value whose description best matches the stated purpose.
      // Use the default value when no practical or regulatory purpose is
      // declared or the study is validating a method rather than testing a
      // specific product class. The identity of the test substance alone does
      // not determine this field.

      "procedure_text": "brief description of the procedure, max 30 words,
        in the source language (see the end of this prompt)" or null,
      "procedure_text_evidence": "exact quote from text, MAX 20 WORDS" or null,
      "procedure_text_confidence": "high"|"medium"|"low" or null if procedure_text is null,

      "species": controlled value (see synonyms above) or null,
      "species_evidence": "exact quote from text, MAX 5 WORDS" or null,
      "species_confidence": "high"|"medium"|"low" or null if species is null,

      "animal_counts": {
        "female": integer (explicitly stated) or null,
        "male": integer (explicitly stated) or null,
        "total": integer (explicitly stated, not derived) or null,
        "per_group": integer (explicitly stated) or null
      } or null if no counts are explicitly stated,
      "animal_counts_evidence": "exact quote from text, MAX 15 WORDS" or null,
      "animal_counts_confidence": "high"|"medium"|"low" or null if animal_counts is null,

      "endpoint": the single most specific slug from "Endpoint values" that
        the study measures (e.g. prefer "eye-irritation" over "eye-effects"),
        or null if none fits. Choose by what the study assesses, not by the
        substance tested. Mapping the study to the list is expected here.
      "endpoint_evidence": "exact quote from text, MAX 15 WORDS" or null,
      "endpoint_confidence": "high"|"medium"|"low" or null if endpoint is null,

      "test_system": array of values from "Test system values" or null,
      "test_system_evidence": "exact quote from text, MAX 15 WORDS" or null,
      "test_system_confidence": "high"|"medium"|"low" or null if test_system is null,

      "guideline_ref": the test guideline the protocol follows or cites, in the
        form "TG 420" or "GD 129" (OECD), or null if none is named. Only a
        guideline the experiment is actually performed under; not one that is
        merely mentioned as background or as a method to be replaced.
      "guideline_ref_evidence": "exact quote from text, MAX 15 WORDS" or null,
      "guideline_ref_confidence": "high"|"medium"|"low" or null if guideline_ref is null,

      "regulatory": true if a named regulatory guideline or authority is
        explicitly cited, false if explicitly stated as non-regulatory,
        null if not mentioned,
      "regulatory_evidence": "exact quote from text, MAX 20 WORDS" or null,
      "regulatory_confidence": "high"|"medium"|"low" or null if regulatory is null,

      "notes": "1-2 sentences on anything the structured fields cannot
        represent: secondary experiments, vocabulary gaps, ambiguous animal
        counts, unsupported routes, study designs outside the standard
        taxonomy, etc. null if nothing needs flagging."
    }
  ]
}

Order experiments by centrality to the protocol's stated objective,
or by per-field confidence if centrality is unclear.

CRITICAL: All _evidence fields must be short, exact quotes (maximum 15–20 words).
Do not quote entire paragraphs.

CRITICAL: Your response must be syntactically complete JSON. Close all strings,
objects, and arrays before ending output.

Detected source language: {source_language}. Keep extracted free-text
(study_type, procedure_text, notes, evidence quotes) in that language.

Protocol description:
{protocol_text}"""


def _endpoint_values_block() -> str:
    from app.services.vocabulary import endpoint_prompt_lines

    lines = endpoint_prompt_lines()
    if not lines:
        return "Endpoint values: not available; return null for endpoint."
    return (
        "Endpoint values (slug: name; indentation shows the hierarchy, deeper = more "
        "specific). Use a slug exactly as written:\n" + lines
    )


def build_extraction_prompt(protocol_text: str, *, source_language: str = "English") -> str:
    from app.services.vocabulary import DEFAULT_APPLICATION, application_prompt_lines

    template = EXTRACTION_PROMPT_TEMPLATE.replace(
        "{application_values}",
        f"Application values (slug: description; default {DEFAULT_APPLICATION}):\n"
        + application_prompt_lines(),
    ).replace("{endpoint_values}", _endpoint_values_block())
    return template.replace(
        "{protocol_text}",
        protocol_text.strip(),
    ).replace("{source_language}", source_language)
