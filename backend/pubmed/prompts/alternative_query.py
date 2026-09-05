"""Prompt that drives both parallel search paths:

Path A — Endpoint/hypothesis: a neutral description of the biological question being
answered. Used to retrieve literature about ANY method that studies this endpoint,
regardless of whether it involves animals.

Path B — Reconstruction: three concrete alternative method descriptions, one per 3R
class. Each is embedded independently and searched against the knowledge base to find
papers describing those specific approaches. Replacement is emphasised most.
"""

ALTERNATIVE_QUERY_PROMPT_TEMPLATE = """You are an expert in the 3Rs framework (Replace, Reduce, Refine)
and alternative methods in biomedical and preclinical research.

Analyze the research protocol below. Your output will drive TWO PARALLEL literature searches.

CRITICAL: The protocol may contain MULTIPLE distinct animal testing procedures (e.g. an acute
LD50 study AND a 28-day repeated-dose study with organ histology and blood biochemistry).
Your descriptions must cover ALL animal testing components — not just the first or most
prominent one. If there is a repeated-dose or subacute component, it is equally important
to address as the acute component.

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
        that could fully replace the animal procedure. Focus on the REPLACEMENT DEVICE
        OR TECHNIQUE NAME and how it works — not on the biology of the animal being replaced.
        Name specific devices, membranes, systems, assay names, validated protocols, or
        regulatory guidelines where known. Do NOT add unrelated cell biology (cell lines,
        receptors, signalling) unless those are the actual replacement method.
        This is the most important field — be as technically specific as possible."
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
        Include non-invasive monitoring, anaesthesia protocols,
        or validated welfare scoring systems."
    }}
  ]
}}

CRITICAL: The replacement description carries the most weight in the subsequent search.
Make it the most specific and technically detailed of the three.
Focus it on the PRIMARY animal procedure being replaced — typically the most acute or
direct animal test. Subacute and organ-specific components are handled by separate
dedicated search queries, so do not dilute the replacement description by trying to
cover all endpoints at once.

KNOWLEDGE BASE VOCABULARY — use these terms where relevant to improve literature retrieval:
- 3Rs / general: "alternative method", "non-animal", "animal-free", "new approach method (NAM)",
  "replacement method"
- In vitro / organotypic: "organoid", "organ-on-a-chip", "microphysiological system",
  "3D cell culture", "spheroid", "air-liquid interface", "iPSC-derived", "induced pluripotent stem cell"
- Computational / in silico: "in silico", "QSAR", "quantitative structure-activity relationship",
  "read-across", "adverse outcome pathway (AOP)", "PBPK", "physiologically based pharmacokinetic",
  "computational toxicology", "machine learning toxicity prediction", "molecular docking",
  "systems biology model", "network pharmacology"
- Omics / molecular profiling: "RNA-seq", "transcriptomics", "gene expression profiling",
  "proteomics", "metabolomics", "toxicogenomics", "mechanistic biomarker", "pathway analysis"
{endpoint_vocabulary}"""

# Vocabulary sections injected only when the protocol matches that endpoint category
_VOCAB_BY_ENDPOINT: dict[str, str] = {
    "skin_irritation": '- Skin irritation/corrosion: "EpiDerm", "EpiSkin", "SkinEthic RHE", "TER assay", "OECD 431", "OECD 439", "reconstructed human epidermis"',
    "skin_corrosion":  '- Skin irritation/corrosion: "EpiDerm", "EpiSkin", "SkinEthic RHE", "TER assay", "OECD 431", "OECD 439", "reconstructed human epidermis"',
    "ocular_irritation": '- Eye irritation: "BCOP", "bovine corneal opacity permeability", "isolated chicken eye", "HET-CAM", "EpiOcular", "EVEIT"',
    "skin_sensitisation": '- Skin sensitisation: "DPRA", "direct peptide reactivity assay", "KeratinoSens", "h-CLAT", "ARE-Nrf2", "GARD assay", "U-SENS", "OECD 442"',
    "genotoxicity": '- Genotoxicity: "Ames test", "in vitro micronucleus", "comet assay", "ToxTracker", "γH2AX", "OECD 471", "OECD 487"',
    "phototoxicity": '- Phototoxicity: "3T3 NRU", "neutral red uptake phototoxicity", "OECD 432", "ROS assay", "reconstructed skin phototoxicity"',
    "pyrogenicity": '- Pyrogenicity: "monocyte activation test (MAT)", "recombinant Factor C", "human whole blood test", "PyroDetect", "OECD 432"',
    "skin_absorption": '- Skin absorption: "Franz cell", "PAMPA", "Caco-2 permeability", "diffusion cell", "OECD 428", "Strat-M membrane"',
    "acute_toxicity": (
        '- Acute toxicity: "zebrafish embryo toxicity", "FET test", "OECD 236", "fixed dose procedure",\n'
        '  "up-and-down procedure", "starting dose procedure", "ICE50 in vitro", "cytotoxicity LD50 prediction"\n'
        '- Subacute / repeated-dose toxicity: "OECD 407", "28-day repeated dose", "subacute toxicity in vitro",\n'
        '  "repeated dose toxicity alternative", "toxicogenomics organ profiling", "multi-organ microphysiological"\n'
        '- Organ-specific in vitro models: "HepaRG cells", "3D liver spheroid", "liver-on-chip",\n'
        '  "RPTEC", "kidney organoid", "iPSC-derived cardiomyocytes", "hERG assay",\n'
        '  "neurosphere assay", "body-on-chip"'
    ),
}


def build_alternative_query_prompt(
    protocol_text: str,
    endpoint_category: str | None,
    study_domain: str,
    species: str | None,
    route: list[str] | None,
    procedure_text: str | None,
    vocabulary: str = "",
) -> str:
    return ALTERNATIVE_QUERY_PROMPT_TEMPLATE.format(
        protocol_text=protocol_text.strip(),
        endpoint_category=endpoint_category or "not specified",
        study_domain=study_domain,
        species=species or "not specified",
        route=", ".join(route) if route else "not specified",
        procedure_text=procedure_text or "not specified",
        endpoint_vocabulary=vocabulary,
    )
