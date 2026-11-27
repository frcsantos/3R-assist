"""Basic science domain profile.

Covers protocols studying biological mechanisms, signalling pathways, cell biology,
developmental biology, or tissue function without a specific clinical disease replacement
target. Examples: thymic T cell selection, stem cell differentiation, signal transduction,
gene regulatory mechanisms, immunological development, tissue homeostasis.
"""

from pubmed.models.analysis import LLMProposedAlternative
from pubmed.skills.base import DomainProfile

# ── Vocabulary ────────────────────────────────────────────────────────────────

BASIC_SCIENCE_VOCABULARY = """KNOWLEDGE BASE VOCABULARY — use these terms where relevant to improve literature retrieval:
- 3Rs / general: "alternative method", "non-animal", "animal-free", "new approach method (NAM)",
  "replacement method", "in vitro model", "animal-free recapitulation"
- Tissue-specific models: for each primary cell type, organ, or tissue mentioned in the
  protocol, derive the matching in vitro alternative — name it specifically (e.g.
  "[tissue] organoid", "iPSC-derived [cell type]", "[tissue]-on-chip",
  "primary [cell type] culture", "ex vivo [tissue] explant"). Do not use generic
  terms like "organoid" alone; always qualify with the tissue from the protocol.
- iPSC and primary cell models: "iPSC-derived", "induced pluripotent stem cell",
  "directed differentiation", "primary cell culture", "stem cell differentiation in vitro",
  "CRISPR-edited human cell line", "inducible knockout cell line"
- 3D and co-culture models: "organoid", "organ-on-a-chip", "microphysiological system",
  "3D cell culture", "spheroid", "air-liquid interface", "organotypic culture",
  "co-culture model", "immune-stromal co-culture", "epithelial-immune interaction in vitro",
  "3D niche model", "self-organising 3D model"
- Gene editing and functional genomics: "CRISPR-Cas9 knockout", "CRISPR screen",
  "gene knockdown", "siRNA knockdown", "shRNA knockdown", "RNAi screen",
  "CRISPRi CRISPRa gene regulation", "base editing prime editing human cell"
- Omics and molecular profiling: "RNA-seq", "transcriptomics", "single-cell RNA-seq",
  "spatial transcriptomics", "proteomics", "metabolomics", "epigenomics",
  "ChIP-seq", "ATAC-seq", "multi-omics integration", "gene regulatory network",
  "pathway analysis", "bulk RNA-seq human tissue"
- Computational / in silico: "in silico", "systems biology", "signalling network model",
  "mathematical model", "agent-based model", "computational biology"
- Lower organism models: "C. elegans", "Drosophila", "zebrafish larvae",
  "invertebrate model", "lower organism replacement\""""

# ── Ranking guidance ──────────────────────────────────────────────────────────

BASIC_SCIENCE_RANK_GUIDANCE = """
CLASSIFICATION RULE — apply before assigning three_r_class:
  Ask: what is the primary experimental system this paper proposes?
  - Non-animal system (cell culture, organoid, in silico, reconstructed tissue) → "replacement"
  - Fewer animals of the same type, or statistical optimisation → "reduction"
  - Procedural welfare improvement, or lower-organism model → "refinement"
  The subject of the biology does not determine the class — the experimental system does.

ALWAYS include:
  - In vitro or 3D models that recapitulate the specific cell type, tissue, or biological
    process in the protocol — the model must match the tissue, not be a generic organoid
  - iPSC-derived or primary cell-based models of the exact cell type under study
  - Co-culture models reproducing the key cellular interactions described in the protocol
  - Computational or systems biology models of the same signalling pathway or mechanism

INCLUDE when relevant:
  - Lower-organism models (C. elegans, Drosophila, zebrafish) for the same conserved mechanism
  - Omics or single-cell approaches on human or in vitro material replacing animal tissue
  - Ex vivo tissue explant or organotypic culture as a bridging model

EXCLUDE:
  - Papers reporting animal experiment results without proposing an in vitro or computational
    alternative to the specific biological mechanism under study
  - Generic iPSC, organoid, or organ-on-chip review papers that survey the technology
    broadly without describing a method for the specific cell type or tissue in this
    protocol. "Could theoretically be adapted" is not sufficient — the paper must actually
    demonstrate or validate the method for the relevant cell type or a closely related one.
  - Disease-specific clinical papers unrelated to the biological mechanism being studied
  - Technology or instrumentation papers (imaging, microfluidics hardware, phenotyping
    platforms) that use zebrafish or invertebrates as example subjects but do not study
    the same biological mechanism as the protocol
  - Lower-organism papers where the organism is used as a generic in vivo model and the
    conserved mechanism under study in the protocol is not demonstrated in that organism

Be strict on replacement and reduction: a paper must describe a method that reduces or
replaces animal use in studying the specific biological mechanism — not merely report findings
from animal studies.
For refinement: a paper qualifies if it describes a concrete procedural improvement —
anaesthesia, analgesia, welfare assessment, non-invasive sampling, or housing optimisation —
applicable to the species and experimental procedure used in this protocol. It does not need
to study the same biological mechanism."""

# ── Always-on Path B injections (method-embedding searches) ──────────────────
# Descriptions are intentionally tissue-agnostic — the LLM-generated alternatives
# (from build_alternative_query_prompt) cover tissue-specific Path B queries.
# These provide baseline coverage of the three main replacement classes.

_IPSC_PATH_B = LLMProposedAlternative(
    three_r_class="replacement",
    method_description=(
        "iPSC-derived and primary cell models replacing animal cell types in mechanistic biology: "
        "directed differentiation of iPSC into the target cell type or tissue; "
        "CRISPR-edited human cell line recapitulating the gene knockout or variant; "
        "patient-derived primary cell culture of the relevant cell type; "
        "stem cell-derived model maintaining cell-type-specific identity and function; "
        "genetically defined in vitro model of the biological mechanism."
    ),
)

_ORGANOID_PATH_B = LLMProposedAlternative(
    three_r_class="replacement",
    method_description=(
        "3D organoid, co-culture, and organ-on-chip models replacing in vivo mechanism studies: "
        "tissue-specific 3D organoid recapitulating the biological process and cell niche; "
        "self-organising 3D model maintaining tissue architecture and cell-type composition; "
        "co-culture model replicating the key cellular interactions under study; "
        "organ-on-chip microphysiological system reproducing tissue-level function."
    ),
)

_REDUCTION_PATH_B = LLMProposedAlternative(
    three_r_class="reduction",
    method_description=(
        "Lower-organism and reduction strategies for basic science protocols: "
        "zebrafish larvae model for conserved biological mechanism at reduced animal scale; "
        "C. elegans or Drosophila model for genetic or signalling pathway screening; "
        "ex vivo tissue explant or precision-cut tissue slice replacing in vivo endpoint; "
        "high-throughput in vitro assay to rank candidates and reduce mammalian animal use."
    ),
)

# ── Always-on Path A injections (endpoint-embedding searches) ─────────────────

_ORGANOID_MECHANISM_INJECTION = (
    "Organoid, 3D tissue model, or organ-on-chip recapitulating the specific biological "
    "mechanism or tissue under study as animal-free replacement: "
    "tissue-specific 3D organoid or microphysiological system; "
    "self-organising 3D model of the target cell niche or tissue; "
    "patient-derived or iPSC-derived organoid of the relevant tissue; "
    "co-culture model replicating key cellular interactions in the biological process; "
    "organotypic culture maintaining tissue-specific architecture and function."
)

_IPSC_PRIMARY_INJECTION = (
    "iPSC-derived and primary cell models replacing animal cell types or tissue: "
    "directed differentiation of iPSC into the target cell type; "
    "patient-derived primary cell culture of the relevant cell type; "
    "stem cell-derived model maintaining cell-type-specific identity and function; "
    "CRISPR-edited human cell line recapitulating the gene variant or knockout; "
    "genetically defined in vitro model of the biological mechanism."
)

_COMPUTATIONAL_INJECTION = (
    "Computational and systems biology models replacing animal mechanism studies: "
    "mathematical or agent-based model of the biological pathway or signalling network; "
    "systems biology network analysis of the relevant molecular interactions; "
    "single-cell RNA-seq transcriptomics proteomics on human or in vitro material "
    "replacing animal tissue endpoint; "
    "bioinformatics pathway analysis of gene regulatory or signalling mechanisms."
)

_REDUCTION_INJECTION = (
    "Lower-organism and reduction strategies for basic science protocols: "
    "C. elegans or Drosophila model of the conserved biological mechanism; "
    "zebrafish larvae model for genetic or mechanistic screening at reduced animal scale; "
    "ex vivo tissue explant or precision-cut tissue slice replacing in vivo endpoint; "
    "high-throughput in vitro screening to reduce mammalian animal numbers."
)

# ── Profile ───────────────────────────────────────────────────────────────────

BASIC_SCIENCE_PROFILE = DomainProfile(
    name="basic_science",
    vocabulary=BASIC_SCIENCE_VOCABULARY,
    base_path_b=[],
    base_path_a=[],
    rank_guidance=BASIC_SCIENCE_RANK_GUIDANCE,
)
