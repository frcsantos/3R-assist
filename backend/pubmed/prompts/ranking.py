RANKING_PROMPT_TEMPLATE = """You are an expert in the 3Rs framework for animal research ethics.

A researcher submitted the following protocol. Your task is to evaluate candidate scientific
papers that may offer alternatives, refinements, or reductions to the animal procedure described.

PROTOCOL ENDPOINT: {endpoint_category}
PROTOCOL STUDY DOMAIN: {study_domain}
PROTOCOL PROCEDURE: {procedure_text}
PROTOCOL FULL OBJECTIVES: {endpoint_hypothesis}

PRE-SCREEN (apply before evaluating any paper):
Does this paper use the SAME animal species as the protocol without proposing a method
to reduce animal numbers OR improve animal welfare? If yes: "include": false.
A mouse study on the same biology is never an alternative to a mouse protocol.
Topic relevance alone does not make a paper a 3Rs alternative.

ALWAYS INCLUDE as refinement (three_r_class: "refinement", include: true):
Papers about anesthesia, analgesia, non-invasive monitoring, welfare assessment, housing
improvements, or validated welfare scoring applicable to the protocol's species. These
improve the animals' welfare without reducing numbers — they are valid refinements by
definition. Do not apply the pre-screen exclusion to these papers.

REPLACEMENT GUARD — before assigning three_r_class "replacement", ask: what is the
primary experimental system this paper describes? If the answer is any kind of living
animal — regardless of how relevant the topic is — it cannot be replacement.
Topical similarity to the protocol is not evidence of an alternative method.

CANDIDATE PAPERS (ordered by semantic similarity):
{candidates_block}

For EVERY paper in the list above, produce one JSON entry — including papers that fail
the pre-screen (set include: false for those). Do NOT skip any paper.

For each paper determine:
1. Does it propose a method to avoid, reduce, or improve animal use in this protocol?
2. Which 3R class does it best represent? (replacement / reduction / refinement)
3. Does it address the same endpoint_category as the protocol?

Return ONLY valid JSON. No preamble. No markdown.

{{
  "ranked": [
    {{
      "index": <integer — the [N] number from the candidate list above>,
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
- "replacement": the paper describes or validates a method that uses ZERO animals of any kind.
  This means no vertebrates, no fish (zebrafish, danio), no invertebrates (C. elegans,
  Drosophila), no embryos used as animal models. Truly animal-free only.
  Valid examples: in vitro cell assay, cell line, organoid, organ-on-chip, reconstructed
  tissue, QSAR, in silico model, computational simulation (PBPK, ML, docking), any NAM.
  Omics (RNA-seq, proteomics, etc.) qualify ONLY when performed on animal-free material
  (human cell lines, patient samples, in vitro cultures) — NOT on animal-derived tissue.
  A paper that used animals only to VALIDATE an otherwise animal-free method still qualifies.
  DOES NOT QUALIFY as replacement — any paper that uses ANY living organism as an
  experimental model, including: mice, rats, zebrafish, fish, C. elegans, Drosophila,
  or any other animal, regardless of how "alternative" or "lower-order" it is described.
- "reduction": the paper achieves the same scientific goal using FEWER mammalian animals
  (e.g. Fixed Dose Procedure, Up-and-Down Procedure, statistical designs, sequential
  testing, dose-sharing). Also applies to omics or mechanistic studies on animal-derived
  samples that demonstrably reduce further animal use. Animals are still used.
- "refinement": use this for papers that either (a) improve welfare in an in vivo study
  (anaesthesia, housing, non-invasive sampling, welfare scoring), OR (b) use a lower-order
  organism (zebrafish, C. elegans, Drosophila, other invertebrates or small vertebrates)
  as a partial alternative to a mammalian model. Lower-order organisms are living animals
  and can never be "replacement" — classify them as "refinement".
DECISION RULE: If the paper uses ANY living animal, it is reduction or refinement — never
replacement. Only choose replacement for methods with zero animal use.

EXCLUDE — set "include": false for ANY of these:
1. Papers using the SAME animal species as the protocol without reducing animal numbers.
   A study using the same species (e.g. mouse study as an alternative to a mouse protocol)
   is FORBIDDEN as an alternative unless it explicitly proposes a method to reduce the
   number of animals of that species. Using the same animal to study the same biology is
   not an alternative — it is just more of the same animal use.
2. Papers that appear to describe the SAME experiment as the submitted protocol
   (same gene, same animal model, same experimental system). If a paper looks like it
   could BE the source of the protocol rather than an alternative to it, exclude it.
3. Papers that report animal study findings without proposing an alternative, replacement,
   or reduction method — including knockout/transgenic studies, genetic deletion
   experiments, and mechanistic animal studies that do not explicitly propose a
   non-animal or reduced-animal approach.
4. Papers studying the same biology in animals as characterisation or basic research —
   these are NOT refinements unless the paper specifically proposes a concrete procedural
   improvement (e.g. non-invasive monitoring, validated welfare scoring, anaesthesia
   protocol). Being topically related to the protocol is not sufficient.

REFINEMENT requires an explicit, actionable procedural improvement to the animal
experiment. A mouse study on the same gene or pathway is NOT a refinement of another
mouse study — it is simply more animal use."""


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
        blocks.append(
            f"════ PAPER [{i}] ════\n"
            f"Title: {c['title']}\n"
            f"Abstract: {c['abstract_text']}\n"
            f"════ END [{i}] ════"
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
