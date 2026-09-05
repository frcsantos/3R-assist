"""Autoimmune and autoinflammatory disease domain profile.

Covers protocols studying: rheumatoid arthritis (RA), systemic lupus erythematosus (SLE),
inflammatory bowel disease (Crohn's disease, ulcerative colitis), psoriasis, Sjögren's
syndrome, ankylosing spondylitis, autoimmune thyroid disease (Hashimoto's, Graves'),
myasthenia gravis, systemic sclerosis (scleroderma), vasculitis, pemphigus, celiac disease,
antiphospholipid syndrome, autoimmune hepatitis, and other conditions driven by
dysregulated adaptive immunity or autoantibody production.

Key 3Rs context: the dominant animal models (collagen-induced arthritis, DSS colitis,
EAE for MS, MRL/lpr lupus mice) are widely used but poorly predictive in humans;
validated human immune cell assays, patient-derived cells, organoids, and joint/gut-on-chip
systems increasingly replace or reduce these.
"""

from pubmed.models.analysis import LLMProposedAlternative
from pubmed.skills.base import DomainProfile

# ── Vocabulary ────────────────────────────────────────────────────────────────

AUTOIMMUNE_VOCABULARY = """KNOWLEDGE BASE VOCABULARY — use these terms where relevant to improve literature retrieval:
- 3Rs / general: "alternative method", "non-animal", "animal-free", "new approach method (NAM)",
  "replacement method", "human immune cell assay", "patient-derived immune model"
- Human immune cell assays: "PBMC stimulation assay", "peripheral blood mononuclear cell assay",
  "T cell activation assay", "T cell proliferation assay", "mixed lymphocyte reaction",
  "Th17 polarisation assay", "Treg induction assay", "Th1 Th2 differentiation in vitro",
  "B cell differentiation assay", "autoantibody production in vitro",
  "dendritic cell maturation assay", "macrophage polarisation M1 M2 assay",
  "neutrophil activation assay", "NETosis assay", "inflammasome assay in vitro",
  "complement activation assay", "NK cell cytotoxicity assay"
- Patient-derived cell models: "patient-derived synoviocyte", "fibroblast-like synoviocyte FLS",
  "rheumatoid arthritis FLS assay", "patient-derived PBMC autoimmune",
  "iPSC-derived T cell", "iPSC-derived macrophage autoimmune",
  "patient-derived intestinal organoid IBD", "colonic organoid Crohn ulcerative colitis",
  "patient-derived keratinocyte psoriasis", "ex vivo synovial tissue culture"
- Organoids and 3D models: "intestinal organoid IBD", "colonic organoid ulcerative colitis",
  "gut organoid Crohn's disease", "gut-on-chip inflammatory bowel disease",
  "joint-on-chip rheumatoid arthritis", "synovial joint organoid",
  "skin organoid psoriasis", "3D skin model psoriasis",
  "thyroid organoid autoimmune thyroiditis", "liver organoid autoimmune hepatitis",
  "airway organoid Sjögren's",
  "co-culture immune cell epithelial cell barrier model"
- Cytokine and signalling assays: "TNF-alpha assay", "IL-6 assay autoimmune",
  "IL-17 assay", "IL-23 assay", "IFN-gamma assay", "IL-1beta inflammasome assay",
  "JAK STAT signalling assay", "NF-κB assay autoimmune",
  "TGF-beta Treg induction assay", "CXCL10 IP-10 autoimmune assay",
  "cytokine multiplex assay PBMC", "cytokine release assay autoimmune"
- Autoantibody and antigen assays: "anti-citrullinated protein antibody ACPA assay",
  "anti-CCP antibody assay", "antinuclear antibody ANA assay",
  "anti-dsDNA antibody assay lupus", "anti-Sm antibody SLE",
  "autoantibody ELISA", "peptidylarginine deiminase PAD assay",
  "citrullination assay in vitro", "tissue transglutaminase assay celiac",
  "acetylcholine receptor antibody myasthenia"
- Ex vivo / tissue: "ex vivo synovial tissue culture RA",
  "ex vivo intestinal biopsy culture IBD", "ex vivo skin biopsy psoriasis",
  "ex vivo thyroid tissue culture", "precision-cut liver slice autoimmune hepatitis"
- Computational / in silico: "systems biology autoimmune signalling",
  "machine learning autoimmune biomarker prediction",
  "network analysis immune cell interaction", "GWAS autoimmune disease susceptibility",
  "single-cell RNA-seq immune cell autoimmune", "mathematical model immune tolerance",
  "in silico drug target JAK inhibitor biologic", "molecular docking JAK STAT",
  "computational T cell receptor epitope prediction",
  "adverse outcome pathway autoimmunity", "transcriptomics autoimmune PBMC"
- Lower organism models: "zebrafish inflammation model",
  "zebrafish autoimmune intestinal", "zebrafish colitis model",
  "Drosophila innate immunity autoimmune", "C. elegans inflammation pathway\""""

# ── Ranking guidance ──────────────────────────────────────────────────────────

AUTOIMMUNE_RANK_GUIDANCE = """
ALWAYS include (cross-cutting for any autoimmune or autoinflammatory protocol):
  - Human PBMC or purified T/B cell assays (activation, proliferation, Th17/Treg
    polarisation, cytokine release) as replacements for in vivo immune challenge models
  - Patient-derived immune cells (synoviocytes, PBMCs, intestinal biopsies) from
    autoimmune patients replacing animal disease models
  - Organoids or gut-on-chip for intestinal autoimmune/inflammatory disease (IBD,
    Crohn's, ulcerative colitis) replacing DSS or TNBS colitis rodent models
  - Cytokine and signalling pathway assays (TNF-α, IL-6, IL-17, IL-23, JAK/STAT,
    NF-κB) as in vitro endpoints replacing in vivo inflammatory readouts
  - Computational approaches: systems biology of immune signalling, ML autoimmune
    biomarker prediction, molecular docking for JAK inhibitors or biologics

INCLUDE when relevant to this specific disease or study objective:
  - Fibroblast-like synoviocyte (FLS) assay or joint-on-chip for rheumatoid arthritis protocols
  - Autoantibody assays (ACPA/anti-CCP, ANA, anti-dsDNA) as in vitro readouts for RA or SLE
  - 3D skin model or keratinocyte/T cell co-culture for psoriasis protocols
  - Intestinal organoid or ex vivo biopsy culture for IBD (Crohn's, UC) protocols
  - iPSC-derived macrophages or dendritic cells for myeloid-driven autoimmune protocols
  - Complement activation or NETosis assay for lupus or vasculitis protocols
  - Thyroid organoid or ex vivo thyroid tissue for Hashimoto's/Graves' protocols
  - Tissue transglutaminase assay or intestinal organoid for celiac disease protocols
  - Single-cell RNA-seq or transcriptomics on patient-derived immune cells or organoids
    replacing animal tissue endpoints
  - Zebrafish colitis or inflammation model as lower-organism reduction intermediate

EXCLUDE:
  - Papers reporting results from animal autoimmune models (collagen-induced arthritis CIA,
    DSS colitis, MRL/lpr lupus mice, EAE, K/BxN serum transfer) without proposing an
    alternative, replacement, or reduction method — animal model findings are NOT refinements
  - Papers about clinical autoimmune disease management or patient cohort studies with no
    connection to a replaceable animal experiment

Be strict: a paper must describe or validate a method that replaces, reduces, or refines
animal use in autoimmune research — not merely study immune pathways or autoimmune
biology in animals."""

# ── Always-on Path B injections ───────────────────────────────────────────────

_IMMUNE_CELL_INJECTION = LLMProposedAlternative(
    three_r_class="replacement",
    method_description=(
        "Human immune cell and patient-derived models replacing animal autoimmune models: "
        "PBMC stimulation cytokine release assay as replacement for in vivo immune challenge; "
        "T cell activation proliferation Th17 Treg polarisation in vitro assay; "
        "B cell differentiation autoantibody production assay; "
        "dendritic cell maturation macrophage M1 M2 polarisation assay; "
        "patient-derived fibroblast-like synoviocyte FLS assay for rheumatoid arthritis; "
        "ex vivo synovial tissue culture RA; "
        "iPSC-derived T cell macrophage dendritic cell for autoimmune disease modelling; "
        "neutrophil NETosis complement activation assay for lupus vasculitis; "
        "autoantibody ACPA anti-CCP ANA anti-dsDNA ELISA assay as in vitro endpoint."
    ),
)

_ORGANOID_TISSUE_INJECTION = LLMProposedAlternative(
    three_r_class="replacement",
    method_description=(
        "Organoid, 3D tissue, and organ-on-chip models replacing animal autoimmune disease models: "
        "intestinal organoid colonic organoid patient-derived IBD Crohn's disease "
        "ulcerative colitis as replacement for DSS TNBS colitis rodent models; "
        "gut-on-chip inflammatory bowel disease model; "
        "joint-on-chip synovial joint organoid for rheumatoid arthritis "
        "replacing collagen-induced arthritis CIA mouse; "
        "3D skin model keratinocyte T cell co-culture for psoriasis; "
        "skin organoid psoriasis replacing ear oedema or psoriasiform skin mouse model; "
        "thyroid organoid for Hashimoto's Graves' autoimmune thyroiditis; "
        "liver organoid precision-cut liver slice autoimmune hepatitis; "
        "co-culture immune cell epithelial barrier model intestinal permeability assay."
    ),
)

_COMPUTATIONAL_INJECTION = LLMProposedAlternative(
    three_r_class="replacement",
    method_description=(
        "Computational and in silico models replacing animal studies in autoimmune research: "
        "systems biology network analysis of autoimmune signalling TNF IL-6 IL-17 JAK STAT; "
        "machine learning deep learning autoimmune biomarker prediction from omics or imaging; "
        "molecular docking virtual screening JAK inhibitor biologic target prediction; "
        "mathematical model of immune tolerance regulatory T cell dynamics; "
        "GWAS single-cell RNA-seq transcriptomics on patient-derived immune cells organoids; "
        "adverse outcome pathway AOP framework for drug-induced autoimmunity; "
        "computational T cell receptor TCR epitope autoantigen prediction; "
        "in silico drug-target interaction DMARDs biologics autoimmune."
    ),
)

_REDUCTION_INJECTION = LLMProposedAlternative(
    three_r_class="reduction",
    method_description=(
        "Strategies to reduce mammalian animal use in autoimmune research: "
        "zebrafish larvae colitis or inflammatory bowel model for drug screening "
        "as lower-organism alternative to rodent colitis; "
        "zebrafish inflammation assay for anti-inflammatory compound screening; "
        "Drosophila innate immunity model for inflammatory pathway genetic screening; "
        "C. elegans inflammation pathway model for drug screening; "
        "high-throughput in vitro PBMC or immune cell assay to rank candidates "
        "before in vivo autoimmune model; "
        "ex vivo human biopsy culture to replace chronic rodent model readouts; "
        "adaptive statistical design for CIA DSS or EAE animal experiments."
    ),
)

# ── Profile ───────────────────────────────────────────────────────────────────

AUTOIMMUNE_PROFILE = DomainProfile(
    name="autoimmune",
    vocabulary=AUTOIMMUNE_VOCABULARY,
    base_path_b=[
        _IMMUNE_CELL_INJECTION,
        _ORGANOID_TISSUE_INJECTION,
        _COMPUTATIONAL_INJECTION,
        _REDUCTION_INJECTION,
    ],
    base_path_a=[],
    rank_guidance=AUTOIMMUNE_RANK_GUIDANCE,
)
