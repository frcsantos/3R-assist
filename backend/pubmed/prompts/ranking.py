RANKING_PROMPT_TEMPLATE = """You are an expert in the 3Rs framework for animal research ethics.

A researcher submitted the following protocol. Your task is to evaluate candidate scientific
papers that may offer alternatives, refinements, or reductions to the animal procedure described,
then write a concise synthesis of the best findings.

PROTOCOL ENDPOINT: {endpoint_category}
PROTOCOL STUDY DOMAIN: {study_domain}
PROTOCOL PROCEDURE: {procedure_text}
PROTOCOL FULL OBJECTIVES: {endpoint_hypothesis}

CANDIDATE PAPERS (ordered by semantic similarity):
{candidates_block}

For each paper, determine:
1. Is it relevant to reducing, replacing, or refining the animal use in this protocol?
2. Which 3R class does it best represent? (replacement / reduction / refinement)
3. Does it address the same endpoint_category as the protocol?

Return ONLY valid JSON. No preamble. No markdown.

{{
  "ranked": [
    {{
      "pmid": "the PMID string",
      "relevance_explanation": "1-2 sentences explaining the connection to the protocol endpoint and how it relates to the 3Rs.",
      "three_r_class": "replacement" | "reduction" | "refinement",
      "endpoint_category": one of [acute_toxicity, skin_irritation, skin_corrosion,
        ocular_irritation, skin_sensitisation, phototoxicity, genotoxicity,
        pyrogenicity, skin_absorption] or null,
      "include": true | false,
      "method_group": "1-3 word canonical label using the method's standard name or acronym. Use EXACTLY these labels when the paper fits: 'zebrafish FET', 'HepaRG hepatotoxicity', 'RPTEC nephrotoxicity', 'iPSC cardiomyocyte', 'liver spheroid', 'liver-on-chip', 'fixed dose procedure', 'up-and-down procedure', 'EpiDerm skin', 'BCOP eye'. For ANY computational or in silico method — including QSAR, PBPK, molecular docking, molecular dynamics, machine learning, read-across, cheminformatics, or any other in silico approach — always use 'in silico model'. For any other organoid, organ-on-chip, microphysiological system, or 3D organotypic culture not covered by a specific label above, use 'microphysiological system'. For other methods choose the shortest unambiguous name. Papers about the SAME method MUST share the EXACT same label."
    }}
  ]
}}

{rank_guidance}

3R CLASS DEFINITIONS — apply strictly:
- "replacement": the paper describes or validates a method that uses NO animals at all.
  Examples: in vitro assay, cell line, organoid, organ-on-chip, reconstructed tissue,
  ex vivo tissue, cell-based assay, QSAR, in silico model, computational simulation
  (molecular dynamics, PBPK, machine learning, docking), or any NAM.
  Organ-specific in vitro models qualify: HepaRG / liver spheroids / liver-on-chip
  (hepatotoxicity), RPTEC / kidney organoids (nephrotoxicity), iPSC-cardiomyocytes /
  hERG assay (cardiotoxicity), neurospheres / cortical neurons (neurotoxicity).
  Omics methods (RNA-seq, transcriptomics, DNA-seq, genotyping, proteomics) qualify as
  replacement ONLY when performed on animal-free material (human cell lines, patient
  samples, in vitro cultures) — NOT when animal tissue is the input.
  A paper that used animals only to VALIDATE an otherwise animal-free method still qualifies.
  DOES NOT QUALIFY: a modified in vivo method that still uses animals (e.g. Fixed Dose
  Procedure, Up-and-Down Procedure, sequential testing) — even if called an "alternative".
- "reduction": the paper achieves the same in vivo scientific goal using FEWER animals
  (e.g. Fixed Dose Procedure, Up-and-Down Procedure, statistical designs, sequential
  testing, dose-sharing, pilot study frameworks). Also applies to omics or mechanistic
  studies performed on animal-derived samples that inform and reduce further animal testing.
  Animals are still used.
- "refinement": the paper improves welfare in an in vivo study without reducing animal
  numbers (e.g. anaesthesia, housing improvements, non-invasive sampling, validated welfare scoring).
DECISION RULE: ask "does this method use any animals?" — if yes, it is reduction or
refinement, never replacement. Only choose replacement for genuinely animal-free methods.

EXCLUDE: papers that report in vivo animal study findings without offering an alternative,
replacement, or reduction method. Research results from animal studies are NOT refinements
unless the paper specifically proposes a procedural improvement to the animal experiment
itself (e.g. less invasive technique, non-invasive imaging, reduced surgical trauma).
Set "include": false for these."""


def build_ranking_prompt(
    endpoint_category: str | None,
    study_domain: str,
    procedure_text: str | None,
    candidates: list[dict],
    endpoint_hypothesis: str | None = None,
    rank_guidance: str = "",
) -> str:
    blocks: list[str] = []
    for i, c in enumerate(candidates, start=1):
        abstract_excerpt = c["abstract_text"][:400].rstrip()
        if len(c["abstract_text"]) > 400:
            abstract_excerpt += "..."
        blocks.append(
            f"[{i}] PMID:{c['pmid']}\n"
            f"Title: {c['title']}\n"
            f"Abstract: {abstract_excerpt}"
        )
    return RANKING_PROMPT_TEMPLATE.format(
        endpoint_category=endpoint_category or "not specified",
        study_domain=study_domain,
        procedure_text=procedure_text or "not specified",
        endpoint_hypothesis=endpoint_hypothesis or "not specified",
        candidates_block="\n\n".join(blocks),
        rank_guidance=rank_guidance or (
            "Set \"include\": true when the paper offers evidence to reduce, replace, or "
            "refine the animal use described. Be generous — aim for 10-15 papers. "
            "When in doubt, include."
        ),
    )
