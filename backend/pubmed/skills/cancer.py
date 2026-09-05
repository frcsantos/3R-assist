"""Cancer / oncology domain profile.

Covers any cancer type: solid tumors (glioblastoma, breast, colorectal, lung, pancreatic,
prostate, ovarian, hepatocellular, renal, bladder, melanoma, sarcoma, etc.),
haematological malignancies (leukemia, lymphoma, myeloma), metastasis studies,
cancer therapy (chemotherapy, radiotherapy, immunotherapy, targeted therapy),
tumor microenvironment, angiogenesis, and cancer stem cell research.
"""

from pubmed.models.analysis import LLMProposedAlternative
from pubmed.skills.base import DomainProfile

# ── Vocabulary ────────────────────────────────────────────────────────────────

CANCER_VOCABULARY = """KNOWLEDGE BASE VOCABULARY — use these terms where relevant to improve literature retrieval:
- 3Rs / general: "alternative method", "non-animal", "animal-free", "new approach method (NAM)",
  "replacement method"
- Organoids / 3D models: "tumor organoid", "cancer organoid", "tumoroid", "patient-derived organoid",
  "patient-derived tumor model", "3D tumor spheroid", "multicellular tumor spheroid (MCTS)",
  "hanging drop spheroid", "ultra-low attachment spheroid", "scaffold-based tumor model",
  "tumor-on-a-chip", "cancer-on-a-chip", "organotypic tumor culture", "ex vivo tumor slice"
- Brain / CNS tumors: "neurosphere", "glioblastoma stem cell culture", "patient-derived GSC",
  "glioma neurosphere model", "brain tumor organoid", "cerebral organoid glioblastoma"
- Breast cancer: "MCF-7 spheroid", "MDA-MB-231 3D culture", "breast cancer organoid",
  "mammary organoid", "breast tumor-on-chip"
- Colorectal / GI cancers: "colorectal cancer organoid", "CRC organoid", "intestinal organoid cancer",
  "pancreatic cancer organoid", "PDAC organoid", "gastric cancer organoid"
- Lung cancer: "lung cancer organoid", "non-small cell lung cancer 3D model", "lung tumor spheroid",
  "air-liquid interface cancer model"
- Other solid tumors: "prostate cancer organoid", "ovarian cancer spheroid",
  "hepatocellular carcinoma organoid", "renal cell carcinoma 3D model", "bladder cancer organoid",
  "melanoma spheroid", "sarcoma 3D culture"
- Haematological malignancies: "leukemia cell culture model", "lymphoma 3D model",
  "myeloma spheroid", "AML in vitro model", "CLL patient-derived culture"
- In vitro functional assays: "clonogenic survival assay", "colony formation assay",
  "Matrigel invasion assay", "Boyden chamber invasion", "wound healing scratch assay",
  "tube formation assay in vitro angiogenesis", "flow cytometry apoptosis cancer",
  "MTT MTS WST-1 cell viability assay cancer", "transwell migration cancer"
- Immunotherapy in vitro: "T cell cancer co-culture", "PBMC tumor assay",
  "humanized immune model cancer", "immune checkpoint in vitro assay",
  "CAR-T cell in vitro assay", "NK cell cytotoxicity assay", "antibody-dependent cytotoxicity"
- Computational / in silico: "mathematical tumor growth model", "agent-based cancer simulation",
  "machine learning cancer drug response", "deep learning oncology prediction",
  "tumor growth kinetics model", "computational radiobiology linear-quadratic model",
  "pharmacokinetic cancer model PBPK", "systems biology cancer signalling",
  "bioinformatics tumor genomics TCGA GEO", "network pharmacology cancer",
  "in silico drug sensitivity cancer", "virtual tumor model"
- Omics / molecular: "transcriptomics cancer", "RNA-seq tumor", "single-cell RNA-seq tumor scRNA-seq",
  "proteomics cancer", "genomics tumor mutation", "multi-omics cancer", "TCGA dataset analysis",
  "whole-exome sequencing cancer", "epigenomics cancer", "spatial transcriptomics tumor\""""

# ── Ranking guidance ──────────────────────────────────────────────────────────

CANCER_RANK_GUIDANCE = """
ALWAYS include (cross-cutting for any cancer/oncology protocol):
  - Patient-derived tumor organoids or tumoroids replacing in vivo xenograft or orthotopic models
  - 3D multicellular tumor spheroids (MCTS) as replacements for animal tumor models
  - Computational / mathematical tumor growth models; machine learning cancer drug response prediction;
    computational radiobiology models
  - In vitro functional assays replacing in vivo endpoints: clonogenic colony formation survival,
    Matrigel invasion, tube formation angiogenesis assay, scratch wound migration, apoptosis assays
  - Ex vivo tumor slice or organotypic explant cultures as intermediate alternatives
  - Omics approaches (RNA-seq, single-cell, proteomics) on human samples replacing animal tissue

INCLUDE when relevant to this specific cancer type or study objective:
  - Cancer type-specific organoid models matching the protocol's tumor type
  - Assays specifically matching the protocol's endpoint (e.g. tube formation / VEGF assay for
    angiogenesis protocols; radiation clonogenic assay for radiotherapy protocols; Matrigel invasion
    for metastasis or migration protocols; immune co-culture for immunotherapy protocols)
  - Humanized immune co-culture or PBMC assays for immune response or immunotherapy protocols
  - Human cell line or patient-derived culture models for the same cancer type
  - Statistical or in vitro-guided dose selection designs that reduce animal cohort size

EXCLUDE:
  - Papers that report in vivo animal tumor findings (xenograft, orthotopic, PDX in vivo,
    syngeneic models) without proposing an alternative, replacement, or reduction method —
    research results from animal studies are NOT refinements
  - Papers that only characterise a tumor model biologically without framing it as an alternative
  - Papers about clinical oncology or tumor biology with no connection to a replaceable animal method

Be strict: a paper must describe or validate a method that replaces, reduces, or refines animal
use — not merely study the same cancer type or pathway in animals."""

# ── Always-on Path B injections ───────────────────────────────────────────────

_ORGANOID_INJECTION = LLMProposedAlternative(
    three_r_class="replacement",
    method_description=(
        "Patient-derived tumor organoids and 3D cancer models as replacements for in vivo "
        "xenograft and orthotopic animal tumor studies: patient-derived tumoroids from biopsy "
        "or resection preserving intratumoral heterogeneity; glioblastoma stem cell neurosphere "
        "patient-derived GSC culture; breast cancer organoids MCF-7 MDA-MB-231 3D spheroid; "
        "colorectal CRC organoids; pancreatic PDAC organoids; lung cancer organoids; "
        "prostate cancer organoids; multicellular tumor spheroid MCTS hanging drop "
        "ultra-low attachment; tumor-on-a-chip microphysiological system; "
        "ex vivo organotypic tumor slice culture."
    ),
)

_COMPUTATIONAL_INJECTION = LLMProposedAlternative(
    three_r_class="replacement",
    method_description=(
        "Computational and in silico cancer models replacing animal tumor studies: "
        "mathematical tumor growth regression and kinetics models; agent-based cancer simulation; "
        "machine learning deep learning cancer drug response and sensitivity prediction; "
        "computational radiobiology linear-quadratic cell survival model; "
        "PBPK pharmacokinetic models for cancer drug distribution and dosimetry; "
        "systems biology network pharmacology cancer signalling pathway modelling; "
        "bioinformatics analysis of TCGA GEO human tumour datasets; "
        "in silico tumour microenvironment modelling; single-cell RNA-seq computational analysis "
        "tumour heterogeneity; virtual tumour model for therapy response prediction."
    ),
)

_IN_VITRO_ASSAY_INJECTION = LLMProposedAlternative(
    three_r_class="replacement",
    method_description=(
        "In vitro functional cancer assays replacing animal endpoint measurements: "
        "clonogenic colony formation survival assay for radiation or drug response; "
        "Matrigel or Boyden chamber invasion and migration assay for metastasis; "
        "tube formation assay for in vitro angiogenesis VEGF response; "
        "flow cytometry apoptosis necrosis cell cycle analysis; "
        "MTT MTS WST-1 cell viability proliferation assay; "
        "scratch wound healing migration assay; "
        "T cell NK cell co-culture cytotoxicity assay for immunotherapy; "
        "ELISA multiplex cytokine immune response assay; "
        "FACS Western blot signalling pathway analysis cancer."
    ),
)

_REDUCTION_INJECTION = LLMProposedAlternative(
    three_r_class="reduction",
    method_description=(
        "Strategies to reduce animal numbers in cancer research: "
        "high-throughput in vitro drug screening and dose optimisation before in vivo validation; "
        "ex vivo patient-derived tumor slice assay to prioritise compounds and reduce cohort size; "
        "bioluminescence imaging or MRI longitudinal monitoring of individual animals "
        "enabling within-subject designs and smaller groups; "
        "adaptive statistical design and power calculation for tumour experiments; "
        "in silico dose selection and pharmacokinetic modelling to reduce ranging studies."
    ),
)

# ── Profile ───────────────────────────────────────────────────────────────────

CANCER_PROFILE = DomainProfile(
    name="cancer_oncology",
    vocabulary=CANCER_VOCABULARY,
    base_path_b=[
        _ORGANOID_INJECTION,
        _COMPUTATIONAL_INJECTION,
        _IN_VITRO_ASSAY_INJECTION,
        _REDUCTION_INJECTION,
    ],
    base_path_a=[],
    rank_guidance=CANCER_RANK_GUIDANCE,
)
