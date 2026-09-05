"""Neurodegenerative disease domain profile.

Covers: Alzheimer's disease, Parkinson's disease, Huntington's disease, ALS,
multiple sclerosis, frontotemporal dementia, Lewy body dementia, prion diseases,
spinal muscular atrophy, and other conditions characterised by progressive neuronal loss,
protein aggregation, or neuroinflammation.
"""

from pubmed.models.analysis import LLMProposedAlternative
from pubmed.skills.base import DomainProfile

# ── Vocabulary ────────────────────────────────────────────────────────────────

NEURODEGENERATION_VOCABULARY = """KNOWLEDGE BASE VOCABULARY — use these terms where relevant to improve literature retrieval:
- 3Rs / general: "alternative method", "non-animal", "animal-free", "new approach method (NAM)",
  "replacement method"
- iPSC-derived neural models: "iPSC-derived neurons", "induced pluripotent stem cell neurons",
  "patient-derived iPSC", "iPSC dopaminergic neurons", "iPSC motor neurons",
  "iPSC cortical neurons", "iPSC astrocytes", "iPSC microglia", "iPSC neural progenitor"
- Brain organoids / 3D neural models: "cerebral organoid", "brain organoid", "cortical organoid",
  "midbrain organoid", "choroid plexus organoid", "neural organoid",
  "neurosphere", "3D neural model", "brain-on-chip", "neurovascular unit on chip",
  "blood-brain barrier model in vitro", "BBB model"
- Primary neuronal cultures: "primary hippocampal neurons", "primary cortical neurons",
  "primary dopaminergic neurons", "SH-SY5Y differentiation", "PC12 cell model",
  "primary motor neuron culture", "cerebellar granule neuron culture"
- Protein aggregation assays: "alpha-synuclein aggregation assay", "thioflavin T fluorescence",
  "amyloid beta aggregation in vitro", "tau aggregation assay", "huntingtin aggregation model",
  "TDP-43 aggregation assay", "FUS aggregation model", "FRET aggregation assay",
  "filter trap aggregation assay", "seeding amplification assay"
- Cell-based disease models: "CRISPR neurodegeneration model", "gene-edited neural cell line",
  "overexpression synuclein cell model", "lentiviral transduction neuron",
  "microfluidic neuron compartment", "neurotoxicity in vitro assay",
  "mitochondrial dysfunction neuronal", "oxidative stress neuronal assay"
- Invertebrate / lower organism models: "C. elegans neurodegeneration model",
  "Drosophila neurodegeneration model", "zebrafish neurodegeneration model",
  "C. elegans alpha-synuclein", "Drosophila Parkinson model", "zebrafish Alzheimer model"
- Computational / in silico: "molecular dynamics protein aggregation simulation",
  "in silico amyloid aggregation", "machine learning neurodegeneration biomarker",
  "mathematical model neurodegeneration progression", "agent-based neural circuit model",
  "systems biology neuroinflammation", "bioinformatics brain transcriptomics GTEx",
  "network analysis neurodegeneration", "PBPK CNS drug model blood-brain barrier",
  "deep learning Alzheimer prediction", "structural bioinformatics tau amyloid"
- Omics / molecular: "transcriptomics neurodegeneration", "single-cell RNA-seq brain",
  "proteomics tau amyloid", "metabolomics neurodegeneration", "epigenomics brain aging",
  "spatial transcriptomics brain", "GWAS neurodegeneration", "multi-omics Alzheimer\""""

# ── Ranking guidance ──────────────────────────────────────────────────────────

NEURODEGENERATION_RANK_GUIDANCE = """
ALWAYS include (cross-cutting for any neurodegenerative disease protocol):
  - iPSC-derived neurons (dopaminergic, cortical, motor, or other relevant subtypes)
    as replacements for animal models of neurodegeneration
  - Brain organoids or neural organoids (cerebral, midbrain, cortical) replacing animal CNS models
  - Primary neuronal cultures (hippocampal, cortical, dopaminergic) as in vitro replacements
  - In vitro protein aggregation assays (alpha-synuclein, tau, amyloid-beta, huntingtin, TDP-43)
    replacing animal protein pathology models
  - Computational or mathematical models of neurodegeneration, protein aggregation, or
    neural circuit degeneration
  - C. elegans or Drosophila models used as lower-organism replacements for mammalian models

INCLUDE when relevant to this specific disease or study objective:
  - Disease-specific iPSC or organoid model matching the protocol's condition (e.g. midbrain
    organoid for Parkinson's, cortical organoid for Alzheimer's, motor neuron culture for ALS)
  - Blood-brain barrier model or neurovascular unit on chip for drug delivery or neuroinflammation
  - In vitro neuroinflammation assays (microglia activation, cytokine release) for protocols
    studying neuroinflammatory components
  - Omics approaches (single-cell RNA-seq, spatial transcriptomics, proteomics) on human
    brain tissue or iPSC-derived cells as alternatives to animal tissue analysis
  - Zebrafish larvae models for genetic screening or drug discovery as reduction intermediates

EXCLUDE:
  - Papers that report in vivo animal model findings (transgenic mice, MPTP models, 6-OHDA
    models, AAV injection models) without proposing an alternative, replacement, or reduction
    method — research results from animal studies are NOT refinements
  - Papers that only characterise a transgenic animal model without framing it as an alternative
  - Papers about human clinical neurology or imaging with no connection to a replaceable
    animal experiment

Be strict: a paper must describe or validate a method that replaces, reduces, or refines animal
use — not merely study the same disease pathway or protein in animals."""

# ── Always-on Path B injections ───────────────────────────────────────────────

_IPSC_ORGANOID_INJECTION = LLMProposedAlternative(
    three_r_class="replacement",
    method_description=(
        "iPSC-derived neural cells and brain organoids as replacements for animal models "
        "of neurodegenerative disease: patient-derived iPSC differentiated into dopaminergic "
        "neurons for Parkinson's disease; iPSC cortical neurons for Alzheimer's disease; "
        "iPSC motor neurons for ALS and spinal muscular atrophy; "
        "cerebral organoids cortical organoids midbrain organoids self-organised 3D brain model; "
        "brain-on-chip neurovascular unit microphysiological system; "
        "blood-brain barrier BBB model in vitro; "
        "primary hippocampal cortical dopaminergic neuronal culture; "
        "SH-SY5Y differentiated neuronal model; neurosphere neural progenitor 3D culture."
    ),
)

_AGGREGATION_ASSAY_INJECTION = LLMProposedAlternative(
    three_r_class="replacement",
    method_description=(
        "In vitro protein aggregation and cell-based models of neurodegeneration replacing "
        "animal pathology models: alpha-synuclein aggregation assay thioflavin T fluorescence "
        "for Parkinson's disease; amyloid-beta Abeta42 aggregation tau hyperphosphorylation "
        "ELISA Western blot immunofluorescence for Alzheimer's disease; "
        "huntingtin polyQ aggregation filter trap assay for Huntington's disease; "
        "TDP-43 FUS aggregation model for ALS; seeding amplification assay RT-QuIC; "
        "CRISPR gene-edited neuronal cell line; lentiviral overexpression neurotoxicity assay; "
        "mitochondrial dysfunction oxidative stress neuronal assay; "
        "microfluidic compartmentalised neuron axon model."
    ),
)

_COMPUTATIONAL_INJECTION = LLMProposedAlternative(
    three_r_class="replacement",
    method_description=(
        "Computational and in silico models of neurodegeneration replacing animal studies: "
        "molecular dynamics simulation of protein aggregation amyloid tau alpha-synuclein; "
        "machine learning deep learning biomarker prediction for neurodegeneration progression; "
        "mathematical model of neuronal loss and disease progression; "
        "agent-based model of neural circuit degeneration and spreading pathology; "
        "systems biology neuroinflammation signalling network; "
        "bioinformatics analysis of human brain transcriptomics GTEx Allen Brain Atlas; "
        "PBPK physiologically-based pharmacokinetic model CNS drug distribution; "
        "structural bioinformatics protein misfolding aggregation inhibitor screening."
    ),
)

_REDUCTION_INJECTION = LLMProposedAlternative(
    three_r_class="reduction",
    method_description=(
        "Strategies to reduce mammalian animal use in neurodegeneration research: "
        "C. elegans invertebrate model for genetic screening of neurodegeneration-related genes; "
        "Drosophila melanogaster neurodegeneration model for pathway and drug screening; "
        "zebrafish larvae neurodegeneration model for in vivo drug screening with fewer animals; "
        "high-throughput in vitro compound screening to prioritise candidates before rodent studies; "
        "ex vivo brain slice electrophysiology to replace in vivo electrophysiological endpoints; "
        "adaptive statistical design and power calculation for transgenic animal experiments."
    ),
)

# ── Profile ───────────────────────────────────────────────────────────────────

NEURODEGENERATION_PROFILE = DomainProfile(
    name="neurodegeneration",
    vocabulary=NEURODEGENERATION_VOCABULARY,
    base_path_b=[
        _IPSC_ORGANOID_INJECTION,
        _AGGREGATION_ASSAY_INJECTION,
        _COMPUTATIONAL_INJECTION,
        _REDUCTION_INJECTION,
    ],
    base_path_a=[],
    rank_guidance=NEURODEGENERATION_RANK_GUIDANCE,
)
