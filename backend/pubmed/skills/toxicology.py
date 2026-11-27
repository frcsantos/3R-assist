"""Toxicology safety-testing domain profile.

Covers: acute lethality (LD50, FDP, UDP), subacute / repeated-dose organ toxicity,
skin / eye / sensitisation / genotoxicity / phototoxicity / pyrogenicity / absorption.
"""

from pubmed.skills.base import DomainProfile

# ── Vocabulary ────────────────────────────────────────────────────────────────
# Recovered from the version that was working well before endpoint-conditional
# gating was introduced.  Used only for toxicology protocols so it cannot
# contaminate detection / potency / general searches.

TOXICOLOGY_VOCABULARY = """KNOWLEDGE BASE VOCABULARY — use these terms where relevant to improve literature retrieval:
- 3Rs / general: "alternative method", "non-animal", "animal-free", "new approach method (NAM)",
  "replacement method"
- In vitro / organotypic: "organoid", "organ-on-a-chip", "microphysiological system",
  "reconstructed human epidermis", "3D cell culture", "spheroid", "air-liquid interface",
  "iPSC-derived", "induced pluripotent stem cell"
- Computational / in silico: "in silico", "QSAR", "quantitative structure-activity relationship",
  "read-across", "adverse outcome pathway (AOP)", "PBPK", "physiologically based pharmacokinetic",
  "computational toxicology", "molecular dynamics simulation", "machine learning toxicity prediction",
  "structure-based virtual screening", "molecular docking", "density functional theory",
  "systems biology model", "network pharmacology", "agent-based model"
- Omics / molecular profiling: "RNA-seq", "transcriptomics", "gene expression profiling",
  "DNA-seq", "whole-genome sequencing", "genotyping", "single-cell RNA sequencing", "scRNA-seq",
  "proteomics", "metabolomics", "epigenomics", "ChIP-seq", "ATAC-seq",
  "multi-omics", "toxicogenomics", "mechanistic biomarker", "pathway analysis"
- Skin irritation/corrosion: "EpiDerm", "EpiSkin", "SkinEthic RHE", "TER assay", "OECD 431", "OECD 439"
- Eye irritation: "BCOP", "bovine corneal opacity permeability", "isolated chicken eye",
  "HET-CAM", "EpiOcular", "EVEIT"
- Skin sensitisation: "DPRA", "direct peptide reactivity assay", "KeratinoSens", "h-CLAT",
  "ARE-Nrf2", "GARD assay", "U-SENS", "OECD 442"
- Genotoxicity: "Ames test", "in vitro micronucleus", "comet assay", "ToxTracker", "γH2AX"
- Phototoxicity: "3T3 NRU", "neutral red uptake phototoxicity", "OECD 432"
- Pyrogenicity: "monocyte activation test (MAT)", "recombinant Factor C", "human whole blood test"
- Acute toxicity: "zebrafish embryo toxicity", "FET test", "OECD 236", "fixed dose procedure",
  "up-and-down procedure"
- Repeated dose / subacute toxicity: "OECD 407", "28-day repeated dose", "subacute toxicity in vitro",
  "repeated dose toxicity alternative", "toxicogenomics organ profiling", "multi-organ microphysiological",
  "adverse outcome pathway repeated dose"
- Hepatotoxicity (liver): "HepaRG cells", "primary human hepatocytes", "3D liver spheroid",
  "liver organoid", "hepatocyte sandwich culture", "drug-induced liver injury (DILI)",
  "liver-on-chip", "in vitro hepatotoxicity", "ALT AST biomarker in vitro", "HepG2 cytotoxicity"
- Nephrotoxicity (kidney): "RPTEC", "proximal tubule epithelial cells", "kidney organoid",
  "nephrotoxicity in vitro", "kidney-on-chip", "tubular toxicity assay", "creatinine biomarker in vitro"
- Cardiotoxicity (heart): "iPSC-derived cardiomyocytes", "hERG channel assay",
  "cardiac organ-on-chip", "in vitro cardiotoxicity", "QT prolongation assay",
  "contractility assay cardiomyocytes"
- Neurotoxicity (brain): "neurosphere assay", "iPSC-derived neurons", "cortical neuron culture",
  "SH-SY5Y differentiation", "in vitro neurotoxicity", "neurotoxicity assay DNT"
- General organ / systemic toxicity: "multi-organ chip", "body-on-chip", "organ-specific toxicity biomarkers",
  "tissue-engineered organ model", "omics organ toxicity", "transcriptomics toxicity profiling"
- Skin absorption: "Franz cell", "PAMPA", "Caco-2 permeability", "diffusion cell"
- Botulinum: "cell-based potency assay", "SNAP-25 cleavage", "endopeptidase assay\""""

# ── Ranking guidance ──────────────────────────────────────────────────────────

TOXICOLOGY_RANK_GUIDANCE = """
ALWAYS include (cross-cutting for any toxicology/safety protocol):
  - in silico / computational: QSAR, PBPK, machine learning toxicity prediction,
    read-across, molecular docking, AOP models — include even if the route of
    administration or specific compound differs; the modelling approach is transferable
  - zebrafish embryo / fish embryo toxicity test (FET, OECD TG 236): always include
    as a replacement for acute mammalian lethality testing regardless of compound class;
    do NOT exclude because it replaces fish tests — it is validated as a mammalian LD50 surrogate
  - reduced-animal statistical designs: fixed dose procedure, up-and-down procedure,
    acute toxic class method, sequential testing, dose-range finding
  - omics or mechanistic characterisation that informs whether animal testing is needed

INCLUDE when relevant to this specific endpoint or study domain:
  - validated in vitro or organotypic models for this endpoint
  - organ-specific in vitro toxicity models when the protocol involves systemic /
    repeated-dose / organ toxicity (HepaRG, RPTEC, iPSC-cardiomyocytes, neurospheres)
  - biomarkers or non-invasive readouts that reduce or replace the animal procedure

EXCLUDE when clearly off-topic:
  - papers that only describe, critique, or discuss in vivo LD50 / lethal dose
    methodology without offering an alternative method
  - organ-specific toxicity cell models (HepaRG, RPTEC, iPSC-CM) when the protocol
    is a single-endpoint local tolerance test (skin/eye/sensitisation only)
  - papers on entirely unrelated endpoints with no connection to this study domain

Be generous — aim to include 10-15 papers. When in doubt, include."""

# ── Always-on Path B injections ───────────────────────────────────────────────

_IN_SILICO_QSAR_INJECTION = (
    "QSAR quantitative structure-activity relationship models replacing animal "
    "toxicity testing: chemical descriptor fingerprint toxicity prediction; "
    "structure-activity relationship acute oral toxicity LD50 estimation; "
    "Ames mutagenicity QSAR model; REACH regulation in silico QSAR."
)

_IN_SILICO_ML_DL_INJECTION = (
    "Machine learning deep learning neural network models replacing animal toxicity "
    "testing: convolutional neural network graph neural network toxicity prediction; "
    "random forest gradient boosting ensemble classifiers for LD50 prediction; "
    "transformer models chemical toxicity; deep learning ADMET prediction."
)

_IN_SILICO_PBPK_INJECTION = (
    "PBPK physiologically-based pharmacokinetic modelling replacing animal dosimetry "
    "studies: in vitro to in vivo extrapolation (IVIVE); population PBPK model; "
    "compartmental toxicokinetic model; reverse dosimetry; PBPK-based risk assessment "
    "without animal experiments."
)

_IN_SILICO_READACROSS_AOP_INJECTION = (
    "Read-across chemical category analogue approach and adverse outcome pathway (AOP) "
    "replacing animal toxicity testing: structural analogue read-across prediction; "
    "chemical category grouping OECD; AOP network mechanistic toxicity prediction; "
    "systems biology pathway toxicology without animal data."
)

_IN_SILICO_DOCKING_INJECTION = (
    "Molecular docking virtual screening replacing animal toxicity studies: "
    "structure-based binding affinity prediction; protein-ligand docking toxicity target; "
    "molecular dynamics simulation toxicity mechanism; computational drug-target "
    "interaction toxicity prediction; AutoDock Vina Glide docking toxicology."
)

_FET_INJECTION =(
        "Zebrafish embryo fish embryo toxicity test (FET) OECD TG 236 as replacement "
        "for acute mammalian lethality: Danio rerio embryos exposed to test substance "
        "for 96 hours, mortality and developmental endpoints assessed; validated "
        "non-protected vertebrate alternative to rodent LD50 and acute oral toxicity; "
        "zebrafish embryo acute toxicity whole-embryo assay."
)

# ── Subacute / organ-toxicity extension ──────────────────────────────────────

_SUBACUTE_SIGNALS = (
    "28-day", "28 day", "subacute", "sub-acute", "repeated dose", "repeated-dose",
    "histolog", "hematoxylin", "eosin", " h&e", "histopatholog",
    "hepato", "nephro",
    "ast ", " alt ", " alp ", "creatinine", "bilirubin", "urea nitrogen",
    "serum biochem", "blood biochem", "hematolog", "haematolog",
    "organ weight", "organ histol",
)

_LIVER_MODEL_INJECTION = (
    "In vitro liver hepatotoxicity models replacing animal histopathology: "
    "HepaRG cells 3D primary hepatocyte spheroids liver organoid liver-on-chip "
    "hepatocyte sandwich culture for drug-induced liver injury (DILI); "
    "AST ALT ALP LDH biomarkers in vitro; HepG2 cytotoxicity; "
    "3D HepaRG repeated-dose hepatotoxicity assessment."
)

_KIDNEY_MODEL_INJECTION = (
    "In vitro kidney nephrotoxicity models replacing animal renal histopathology: "
    "RPTEC renal proximal tubule epithelial cells kidney organoid kidney-on-chip "
    "tubular toxicity assay; creatinine urea nitrogen biomarkers in vitro; "
    "3D kidney tubuloid drug-induced nephrotoxicity assessment."
)

_HEART_MODEL_INJECTION = (
    "In vitro cardiac cardiotoxicity models replacing animal heart histopathology: "
    "iPSC-derived cardiomyocytes cardiac organ-on-chip heart-on-chip; "
    "hERG channel assay QT prolongation; contractility beating frequency assay; "
    "3D cardiac spheroid drug-induced cardiotoxicity assessment."
)

_BRAIN_MODEL_INJECTION = (
    "In vitro brain neurotoxicity models replacing animal brain histopathology: "
    "neurosphere assay iPSC-derived cortical neurons brain organoid cerebral organoid; "
    "SH-SY5Y differentiation; DNT developmental neurotoxicity in vitro; "
    "neural network-on-chip drug-induced neurotoxicity assessment."
)

_MULTI_ORGAN_INJECTION = (
    "Multi-organ microphysiological system body-on-chip replacing systemic repeated-dose "
    "animal toxicity with multi-organ histopathology: liver-kidney-heart-brain "
    "interconnected organ chips; human organ-on-chip platform; body-on-chip systemic "
    "toxicity profiling; multi-organ organoid co-culture repeated-dose toxicity."
)

_PRE_LETHALITY_ENDPOINT_INJECTION = (
    "Reduced-animal acute oral toxicity methods: Fixed Dose Procedure OECD TG 420 "
    "evident toxicity endpoint not lethality; Acute Toxic Class method OECD TG 423 "
    "GHS classification stepwise 6 animals; Up-and-Down Procedure OECD TG 425 "
    "sequential dosing LD50 confidence interval 6 animals; basal cytotoxicity "
    "NICEATM GD 129 starting dose estimation in vitro LD50 prediction."
)

# ── Profile ───────────────────────────────────────────────────────────────────

_ACUTE_SIGNALS = (
    "ld50", "dl50", "lethal dose 50", "lethal dose50",
    "acute toxicity", "acute lethality", "acute oral",
    "single dose", "single-dose",
    "fixed dose procedure", "up-and-down procedure", "acute toxic class",
)

TOXICOLOGY_PROFILE = DomainProfile(
    name="toxicology_safety",
    vocabulary=TOXICOLOGY_VOCABULARY,
    base_path_b=[],
    base_path_a=[
        # Computational / in silico replacements (always-on for any tox protocol)
        _IN_SILICO_QSAR_INJECTION,
        _IN_SILICO_ML_DL_INJECTION,
        _IN_SILICO_PBPK_INJECTION,
        _IN_SILICO_READACROSS_AOP_INJECTION,
        _IN_SILICO_DOCKING_INJECTION,
    ],
    acute_signals=_ACUTE_SIGNALS,
    acute_path_a=[
        # In vitro / biological replacements (only for acute lethality protocols)
        _FET_INJECTION,
        _PRE_LETHALITY_ENDPOINT_INJECTION,
    ],
    rank_guidance=TOXICOLOGY_RANK_GUIDANCE,
    subacute_signals=_SUBACUTE_SIGNALS,
    subacute_path_b=[],
    subacute_path_a=[
        _LIVER_MODEL_INJECTION,
        _KIDNEY_MODEL_INJECTION,
        _HEART_MODEL_INJECTION,
        _BRAIN_MODEL_INJECTION,
        _MULTI_ORGAN_INJECTION,
    ],
)
