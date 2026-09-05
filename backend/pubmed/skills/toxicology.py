"""Toxicology safety-testing domain profile.

Covers: acute lethality (LD50, FDP, UDP), subacute / repeated-dose organ toxicity,
skin / eye / sensitisation / genotoxicity / phototoxicity / pyrogenicity / absorption.
"""

from pubmed.models.analysis import LLMProposedAlternative
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

_IN_SILICO_INJECTION = LLMProposedAlternative(
    three_r_class="replacement",
    method_description=(
        "In silico computational toxicology methods replacing animal testing: "
        "QSAR quantitative structure-activity relationship models for toxicity prediction; "
        "PBPK physiologically-based pharmacokinetic modelling for dose-response; "
        "machine learning deep learning toxicity classifiers; molecular docking and "
        "molecular dynamics simulation; read-across and chemical category approaches; "
        "adverse outcome pathway (AOP) network analysis; systems biology toxicity models."
    ),
)

_FET_INJECTION = LLMProposedAlternative(
    three_r_class="replacement",
    method_description=(
        "Zebrafish embryo fish embryo toxicity test (FET) OECD TG 236 as replacement "
        "for acute mammalian lethality: Danio rerio embryos exposed to test substance "
        "for 96 hours, mortality and developmental endpoints assessed; validated "
        "non-protected vertebrate alternative to rodent LD50 and acute oral toxicity; "
        "zebrafish embryo acute toxicity whole-embryo assay."
    ),
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

_ORGAN_MODEL_INJECTION = LLMProposedAlternative(
    three_r_class="replacement",
    method_description=(
        "In vitro organ-specific toxicity models as alternatives to subacute "
        "repeated-dose animal study with histological and biochemical evaluation: "
        "HepaRG cells or 3D primary hepatocyte spheroids for hepatotoxicity "
        "(AST ALT ALP biomarkers); RPTEC proximal tubule cells or kidney organoids "
        "for nephrotoxicity (creatinine urea biomarkers); iPSC-derived cardiomyocytes "
        "or hERG channel assay for cardiotoxicity; neurosphere or cortical neuron "
        "assay for neurotoxicity; multi-organ microphysiological system body-on-chip "
        "for systemic repeated-dose toxicity profiling."
    ),
)

_ORGAN_ENDPOINT_INJECTION = (
    "In vitro hepatotoxicity nephrotoxicity cardiotoxicity neurotoxicity "
    "prediction and assessment: liver cell models ALT AST LDH biomarkers, "
    "kidney tubular toxicity creatinine, cardiac cell viability, "
    "organ-specific cytotoxicity drug-induced organ injury in vitro."
)

# ── Profile ───────────────────────────────────────────────────────────────────

TOXICOLOGY_PROFILE = DomainProfile(
    name="toxicology_safety",
    vocabulary=TOXICOLOGY_VOCABULARY,
    base_path_b=[_FET_INJECTION, _IN_SILICO_INJECTION],
    base_path_a=[],
    rank_guidance=TOXICOLOGY_RANK_GUIDANCE,
    subacute_signals=_SUBACUTE_SIGNALS,
    subacute_path_b=[_ORGAN_MODEL_INJECTION],
    subacute_path_a=[_ORGAN_ENDPOINT_INJECTION],
)
