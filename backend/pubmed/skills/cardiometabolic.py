"""Cardiometabolic disease domain profile.

Covers: cardiovascular diseases (atherosclerosis, coronary artery disease, myocardial
infarction, heart failure, cardiomyopathy, arrhythmia, hypertension) and metabolic
diseases (type 1/2 diabetes, obesity, metabolic syndrome, NAFLD/NASH, insulin resistance,
dyslipidemia) and their intersection.
"""

from pubmed.models.analysis import LLMProposedAlternative
from pubmed.skills.base import DomainProfile

# ── Vocabulary ────────────────────────────────────────────────────────────────

CARDIOMETABOLIC_VOCABULARY = """KNOWLEDGE BASE VOCABULARY — use these terms where relevant to improve literature retrieval:
- 3Rs / general: "alternative method", "non-animal", "animal-free", "new approach method (NAM)",
  "replacement method"
- iPSC-derived cardiac models: "iPSC-cardiomyocyte", "iPSC-derived cardiomyocyte",
  "patient-derived iPSC cardiomyocyte", "cardiac organoid", "heart organoid",
  "engineered heart tissue", "cardiac spheroid", "3D cardiac model",
  "iPSC endothelial cell", "iPSC smooth muscle cell"
- Heart-on-chip / cardiac MPS: "heart-on-chip", "cardiac microphysiological system",
  "cardiac organ-on-chip", "vascularised cardiac organoid",
  "multi-organ chip heart liver", "body-on-chip cardiometabolic"
- Vascular / atherosclerosis in vitro models: "endothelial cell assay",
  "foam cell formation assay", "vascular smooth muscle cell assay",
  "in vitro atherosclerosis model", "LDL oxidation cell assay",
  "transendothelial resistance TEER assay", "aortic ring assay ex vivo"
- Pancreatic / diabetes models: "pancreatic beta cell assay", "islet of Langerhans in vitro",
  "MIN6 beta cell", "INS-1 cell", "human islet in vitro", "glucose-stimulated insulin secretion",
  "insulin secretion assay", "pancreatic organoid", "iPSC-derived pancreatic beta cell"
- Metabolic / obesity models: "3T3-L1 adipocyte differentiation", "adipocyte assay",
  "lipid accumulation assay", "PPAR gamma assay", "adipogenesis in vitro",
  "liver organoid NAFLD NASH model", "hepatocyte steatosis assay",
  "HepaRG steatosis", "lipotoxicity assay", "mitochondrial fatty acid oxidation assay"
- Computational / in silico: "PBPK cardiometabolic model", "cardiac action potential simulation",
  "in silico QT prolongation model", "hERG channel model computational",
  "cardiovascular risk computational model", "machine learning cardiac biomarker",
  "systems biology insulin signalling", "mathematical model glucose homeostasis",
  "agent-based atherogenesis model", "network analysis metabolic syndrome",
  "in silico metabolic flux analysis", "genome-scale metabolic model"
- Lower organism models: "zebrafish heart model", "zebrafish cardiac assay",
  "zebrafish metabolic model", "zebrafish diabetes model", "zebrafish obesity model",
  "C. elegans fat metabolism", "Drosophila cardiac model"
- Omics / molecular: "transcriptomics cardiomyocyte", "single-cell RNA-seq heart",
  "proteomics cardiac", "metabolomics insulin resistance", "lipidomics atherosclerosis",
  "epigenomics cardiac hypertrophy", "GWAS cardiovascular", "multi-omics metabolic syndrome\""""

# ── Ranking guidance ──────────────────────────────────────────────────────────

CARDIOMETABOLIC_RANK_GUIDANCE = """
ALWAYS include (cross-cutting for any cardiometabolic protocol):
  - iPSC-derived cardiomyocytes or cardiac organoids as replacements for in vivo cardiac models
  - Heart-on-chip or cardiac microphysiological systems
  - In vitro endothelial cell or vascular smooth muscle cell assays replacing animal
    vascular models (atherosclerosis, hypertension)
  - Pancreatic beta cell or human islet in vitro assays for diabetes protocols
  - Computational cardiac or metabolic models (action potential simulation, hERG model,
    glucose homeostasis model, cardiovascular risk model)

INCLUDE when relevant to this specific condition or study objective:
  - Cardiac-specific iPSC model matched to the protocol's disease (e.g. iPSC-CMs with
    disease-causing variants for cardiomyopathy, iPSC-CMs hERG assay for arrhythmia)
  - In vitro atherosclerosis or foam cell formation assays for atherogenesis protocols
  - Liver organoid or hepatocyte steatosis assay for NAFLD/NASH or metabolic liver protocols
  - Adipocyte differentiation or adipogenesis assay for obesity protocols
  - Ex vivo aortic ring or Langendorff heart preparation as intermediate alternative
  - Zebrafish cardiac or metabolic model as lower-organism reduction intermediate
  - Omics approaches on human iPSC-derived cells or patient tissue replacing animal endpoints

EXCLUDE:
  - Papers reporting in vivo animal study findings (rodent infarction models, diet-induced
    obesity in mice, transgenic metabolic mice) without proposing an alternative, replacement,
    or reduction method — animal study results are NOT refinements
  - Papers about clinical cardiovascular medicine or epidemiology with no connection to a
    replaceable animal experiment

Be strict: a paper must describe or validate a method that replaces, reduces, or refines
animal use — not merely study the same cardiac or metabolic pathway in animals."""

# ── Always-on Path B injections ───────────────────────────────────────────────

_CARDIAC_MODEL_INJECTION = LLMProposedAlternative(
    three_r_class="replacement",
    method_description=(
        "iPSC-derived cardiomyocytes and cardiac organoids as replacements for animal "
        "cardiac disease models: patient-derived iPSC-cardiomyocytes for cardiomyopathy "
        "arrhythmia heart failure modelling; cardiac organoid engineered heart tissue; "
        "heart-on-chip cardiac microphysiological system; "
        "iPSC-CM contractility calcium transient action potential assay; "
        "hERG channel assay for drug cardiotoxicity; "
        "iPSC endothelial cells vascular smooth muscle cells for cardiovascular models; "
        "ex vivo aortic ring assay; Langendorff isolated perfused heart preparation."
    ),
)

_METABOLIC_ASSAY_INJECTION = LLMProposedAlternative(
    three_r_class="replacement",
    method_description=(
        "In vitro metabolic and pancreatic assays replacing animal models of diabetes, "
        "obesity and metabolic disease: pancreatic beta cell assay glucose-stimulated "
        "insulin secretion GSIS MIN6 INS-1 cells; human islet in vitro culture; "
        "iPSC-derived pancreatic beta cells; pancreatic organoid; "
        "3T3-L1 adipocyte differentiation adipogenesis assay lipid accumulation PPAR-gamma; "
        "HepaRG hepatocyte steatosis assay NAFLD NASH in vitro model; "
        "liver organoid fatty liver model; mitochondrial fatty acid oxidation assay; "
        "lipotoxicity glucotoxicity cell assay."
    ),
)

_COMPUTATIONAL_INJECTION = LLMProposedAlternative(
    three_r_class="replacement",
    method_description=(
        "Computational and in silico models of cardiometabolic disease replacing animal studies: "
        "cardiac action potential computational model QT prolongation simulation; "
        "hERG channel in silico model for drug cardiotoxicity prediction; "
        "PBPK physiologically-based pharmacokinetic model cardiovascular drug; "
        "machine learning deep learning cardiovascular risk biomarker prediction; "
        "mathematical model of glucose insulin homeostasis; "
        "systems biology insulin signalling pathway model; "
        "agent-based model of atherogenesis foam cell; "
        "genome-scale metabolic model GSMM metabolic syndrome; "
        "in silico metabolic flux analysis."
    ),
)

_REDUCTION_INJECTION = LLMProposedAlternative(
    three_r_class="reduction",
    method_description=(
        "Strategies to reduce mammalian animal use in cardiometabolic research: "
        "zebrafish larvae cardiac assay for drug screening as lower-organism model; "
        "zebrafish metabolic obesity diabetes model for genetic or drug screening; "
        "C. elegans fat metabolism assay for metabolic pathway screening; "
        "Drosophila cardiac model for genetic screening; "
        "high-throughput in vitro beta cell or cardiomyocyte screening before in vivo; "
        "adaptive statistical design for metabolic animal experiments; "
        "in silico cardiovascular risk model to reduce dose-ranging animal studies."
    ),
)

# ── Profile ───────────────────────────────────────────────────────────────────

CARDIOMETABOLIC_PROFILE = DomainProfile(
    name="cardiometabolic",
    vocabulary=CARDIOMETABOLIC_VOCABULARY,
    base_path_b=[
        _CARDIAC_MODEL_INJECTION,
        _METABOLIC_ASSAY_INJECTION,
        _COMPUTATIONAL_INJECTION,
        _REDUCTION_INJECTION,
    ],
    base_path_a=[],
    rank_guidance=CARDIOMETABOLIC_RANK_GUIDANCE,
)
