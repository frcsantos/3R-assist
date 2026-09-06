"""Prompt that drives both parallel search paths:

Path A — Endpoint/hypothesis: a neutral description of the biological question being
answered. Used to retrieve literature about ANY method that studies this endpoint,
regardless of whether it involves animals.

Path B — Reconstruction: three concrete alternative method descriptions, one per 3R
class. Each is embedded independently and searched against the knowledge base to find
papers describing those specific approaches. Replacement is emphasised most.
"""

ALTERNATIVE_QUERY_PROMPT_TEMPLATE = """You are an expert in the 3Rs framework (Replace, Reduce, Refine)
and alternative methods in toxicology and biomedical research.

Analyze the research protocol below. Your output will drive TWO PARALLEL literature searches.

═══════════════════════════════════════════════════════════════════
PATH A — ENDPOINT SEARCH
A semantic query describing the biological endpoint or scientific question in neutral
terms (not biased toward animal or non-animal methods). This retrieves all literature
about this endpoint regardless of methodology.
═══════════════════════════════════════════════════════════════════

═══════════════════════════════════════════════════════════════════
PATH B — RECONSTRUCTION SEARCH
Three concrete descriptions of alternative methods that could achieve the same
scientific objective. Each description is embedded and matched independently against
the literature. ORDER AND SPECIFICITY MATTER:
  — Replacement: highest priority, most detail required
  — Reduction: medium priority
  — Refinement: lowest priority
Each description should be specific enough to retrieve real papers (name cell types,
assays, readouts, computational approaches, regulatory models, etc.).
═══════════════════════════════════════════════════════════════════

PROTOCOL:
{protocol_text}

EXTRACTED PARAMETERS:
- Endpoint category  : {endpoint_category}
- Study domain       : {study_domain}
- Species            : {species}
- Route              : {route}
- Procedure          : {procedure_text}

Return ONLY valid JSON. No preamble. No markdown.

{{
  "endpoint_hypothesis": "1-2 sentences describing the core scientific question this
    protocol answers (e.g. 'Determine the acute dermal irritation potential of compound X
    in an in vivo mammalian model').",

  "endpoint_search_query": "2-4 sentences describing the biological endpoint and its
    measurable outcomes, written to retrieve literature about ANY methodology for this
    endpoint. Include key biomarkers, assay readouts, and outcome measures. Do NOT
    mention animals or in vitro — stay neutral.",

  "alternatives": [
    {{
      "three_r_class": "replacement",
      "method_description": "40-80 word description of a specific non-animal method
        (in vitro, ex vivo, organoid, computational, QSAR, microphysiological, etc.)
        that could fully replace the animal procedure for this endpoint. Name specific
        cell types or lines, assay names, readouts, validated protocols, or regulatory
        guidelines where known. This is the most important field — be as technically
        specific as possible."
    }},
    {{
      "three_r_class": "reduction",
      "method_description": "30-60 word description of a specific approach that uses
        the same or similar species but substantially reduces animal numbers. Include
        statistical designs (e.g. sequential testing, ToxicoPrediction-guided dose
        setting), in silico starting point selection, or pilot study frameworks."
    }},
    {{
      "three_r_class": "refinement",
      "method_description": "25-50 word description of a specific procedural refinement
        that minimises pain or distress while achieving the same scientific endpoint.
        Include humane endpoints, non-invasive monitoring, anaesthesia protocols,
        or validated welfare scoring systems."
    }}
  ]
}}

CRITICAL: The replacement description carries the most weight in the subsequent search.
Make it the most specific and technically detailed of the three."""


def build_alternative_query_prompt(
    protocol_text: str,
    endpoint_category: str | None,
    study_domain: str,
    species: str | None,
    route: list[str] | None,
    procedure_text: str | None,
) -> str:
    return ALTERNATIVE_QUERY_PROMPT_TEMPLATE.format(
        protocol_text=protocol_text.strip(),
        endpoint_category=endpoint_category or "not specified",
        study_domain=study_domain,
        species=species or "not specified",
        route=", ".join(route) if route else "not specified",
        procedure_text=procedure_text or "not specified",
    )
