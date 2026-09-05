"""Infectious disease domain profile.

Covers safety and efficacy research protocols for viral, bacterial, parasitic and
fungal pathogens — acute, chronic, and lethal infections — including antimicrobial
drug testing, vaccine development, and host-pathogen interaction studies.

Key 3Rs context: animal challenge and infection models are common in this domain;
validated alternatives include cell-based infection models, organoid/organ-on-chip
infection systems, pseudovirus/replicon platforms, ex vivo human tissue, and
lower-organism models (Galleria, zebrafish, C. elegans).
"""

from pubmed.models.analysis import LLMProposedAlternative
from pubmed.skills.base import DomainProfile

# ── Vocabulary ────────────────────────────────────────────────────────────────

INFECTIOUS_DISEASE_VOCABULARY = """KNOWLEDGE BASE VOCABULARY — use these terms where relevant to improve literature retrieval:
- 3Rs / general: "alternative method", "non-animal", "animal-free", "new approach method (NAM)",
  "replacement method", "animal-free infection model", "validated in vitro infection model"
- Cell-based infection models: "Vero E6 cell infection", "A549 lung cell infection",
  "Calu-3 airway cell infection", "Huh7 hepatocyte infection", "HepaRG hepatitis model",
  "THP-1 macrophage infection model", "primary human macrophage infection",
  "PBMC infection assay", "human monocyte-derived macrophage infection",
  "HepG2 hepatitis model", "Caco-2 intestinal infection model",
  "NCI-H441 airway epithelium infection"
- Organoid and 3D infection models: "intestinal organoid infection",
  "lung organoid infection", "airway organoid SARS-CoV-2",
  "brain organoid viral infection Zika encephalitis",
  "liver organoid hepatitis infection", "cholangiocyte organoid infection",
  "colonic organoid C. difficile", "kidney organoid infection",
  "gut-on-chip infection model", "airway-on-chip respiratory virus",
  "lung-on-chip influenza", "organ-on-chip bacterial infection"
- Air-liquid interface (ALI) models: "air-liquid interface culture respiratory virus",
  "ALI airway epithelium infection", "primary bronchial epithelial cell ALI",
  "MucilAir infection model", "EpiAirway infection"
- Ex vivo models: "ex vivo human lung infection", "ex vivo tonsil infection",
  "ex vivo intestinal explant infection", "ex vivo PBMC infection",
  "precision-cut lung slice PCLS infection"
- Reduced-risk / surrogate virus systems: "pseudovirus assay", "lentiviral pseudoparticle",
  "vesicular stomatitis virus VSV pseudotype",
  "replicon system hepatitis C HCV", "SARS-CoV-2 replicon",
  "virus-like particle VLP", "subunit protein assay",
  "recombinant viral protein binding assay", "neutralisation assay cell-based"
- Antimicrobial susceptibility in vitro: "minimum inhibitory concentration MIC assay",
  "time-kill curve assay", "biofilm formation assay", "biofilm eradication assay",
  "intracellular killing assay macrophage", "checkerboard synergy assay",
  "EUCAST CLSI broth microdilution", "disk diffusion alternative",
  "high-throughput antimicrobial screening", "antimicrobial resistance in vitro"
- Immune function assays: "cytokine release assay", "PBMC cytokine",
  "TLR toll-like receptor assay", "innate immune signalling assay",
  "NLRP3 inflammasome assay", "complement activation assay",
  "neutrophil killing assay", "opsonophagocytosis assay",
  "NK cell cytotoxicity assay infection", "T cell activation assay pathogen"
- Vaccine / immunology in vitro: "in vitro vaccine potency alternative",
  "reverse vaccinology in silico", "VLP vaccine immunogenicity in vitro",
  "dendritic cell activation assay vaccine", "ELISPOT assay vaccine"
- Computational / in silico: "molecular docking antiviral target",
  "in silico antibiotic target", "molecular dynamics viral protein",
  "SIR SEIR epidemiological model", "transmission dynamics model",
  "phylogenetic genomic epidemiology", "reverse vaccinology computational",
  "machine learning antimicrobial resistance prediction",
  "in silico antibiotic PBPK model", "systems biology host-pathogen interaction",
  "GWAS infectious disease susceptibility", "single-cell RNA-seq infection"
- Fungal infection models: "Candida albicans in vitro biofilm", "Candida in vitro virulence assay",
  "Aspergillus fumigatus macrophage killing assay", "antifungal MIC assay",
  "Cryptococcus in vitro infection model", "fungal biofilm eradication assay",
  "EUCAST antifungal susceptibility testing", "macrophage Aspergillus killing assay",
  "Candida HaCaT keratinocyte infection", "oral candidiasis organoid model"
- Protozoan / parasitic models: "Leishmania macrophage killing assay",
  "Trypanosoma in vitro drug assay", "Trypanosoma brucei HTS drug screening",
  "Trypanosoma cruzi intracellular assay", "Plasmodium liver stage hepatocyte model",
  "Plasmodium erythrocyte stage in vitro", "Toxoplasma gondii in vitro model",
  "Cryptosporidium intestinal organoid", "Giardia cell culture assay",
  "schistosomiasis in vitro larval assay", "malaria drug high-throughput screening"
- Lower organism models: "Galleria mellonella infection model",
  "wax moth larvae infection", "zebrafish infection model",
  "zebrafish Mycobacterium marinum", "zebrafish MRSA Staphylococcus",
  "zebrafish Salmonella infection", "zebrafish Candida infection",
  "zebrafish Aspergillus infection", "zebrafish malaria Plasmodium",
  "C. elegans bacterial infection model", "C. elegans Candida fungal model",
  "Drosophila innate immunity infection\""""

# ── Ranking guidance ──────────────────────────────────────────────────────────

INFECTIOUS_DISEASE_RANK_GUIDANCE = """
ALWAYS include (cross-cutting for any infectious disease protocol):
  - Cell-based infection models (primary human macrophages, THP-1, airway epithelial lines,
    hepatocytes) as replacements for animal infection models
  - Organoid or organ-on-chip infection models (intestinal, lung, liver, brain organoids;
    gut-on-chip, airway-on-chip) replacing animal challenge models
  - Pseudovirus, replicon, or virus-like particle (VLP) systems that eliminate the need
    for live-virus animal challenge experiments
  - Computational antiviral/antibiotic drug discovery: molecular docking, molecular dynamics
    of pathogen targets, machine learning for resistance prediction
  - In vitro antimicrobial susceptibility assays (MIC, biofilm, time-kill) replacing animal
    infection dose-finding and efficacy models

INCLUDE when relevant to this specific pathogen or study objective:
  - Air-liquid interface (ALI) airway epithelium culture for respiratory virus protocols
    (influenza, SARS-CoV-2, RSV, rhinovirus)
  - Ex vivo human lung or intestinal tissue for acute lethal or high-pathogenicity protocols
    where organoids are not yet established
  - Precision-cut lung slices (PCLS) as ex vivo alternative to in vivo respiratory infection
  - Macrophage or THP-1 intracellular killing assay for intracellular pathogen protocols
    (Mycobacterium tuberculosis, Leishmania, Salmonella, Listeria)
  - Hepatocyte or liver organoid infection model for hepatitis B/C or Plasmodium liver-stage
  - Brain organoid for neurotropic virus protocols (Zika, herpes encephalitis, enterovirus)
  - Immune function assays (TLR, cytokine, complement, opsonophagocytosis) replacing in vivo
    immune challenge studies
  - Galleria mellonella or zebrafish as lower-organism reduction alternatives for antimicrobial
    efficacy screening before mammalian studies
  - In silico reverse vaccinology or VLP/subunit protein assays for vaccine development protocols
  - Single-cell RNA-seq or transcriptomics on infected human cells or organoids replacing
    animal tissue endpoints

EXCLUDE:
  - Papers reporting in vivo animal infection challenge studies (mouse, ferret, non-human
    primate lethal challenge) without proposing an alternative, replacement, or reduction
    method — animal infection results are NOT refinements
  - Papers about clinical infectious disease management, epidemiology, or patient cohort
    studies with no connection to a replaceable animal experiment

Be strict: a paper must describe or validate a method that replaces, reduces, or refines
animal use in infectious disease research — not merely study pathogen biology or drug
efficacy in animals."""

# ── Always-on Path B injections ───────────────────────────────────────────────

_CELL_ORGANOID_INJECTION = LLMProposedAlternative(
    three_r_class="replacement",
    method_description=(
        "Cell-based and organoid infection models replacing animal challenge studies: "
        "primary human macrophage THP-1 monocyte intracellular infection assay "
        "for Mycobacterium tuberculosis Leishmania Salmonella Listeria; "
        "Vero E6 A549 Calu-3 airway epithelial cell infection for respiratory viruses "
        "SARS-CoV-2 influenza RSV; "
        "HepaRG HepG2 primary hepatocyte Huh7 infection for hepatitis B C; "
        "intestinal organoid infection Clostridioides difficile rotavirus norovirus Salmonella; "
        "lung organoid airway organoid air-liquid interface ALI respiratory virus infection; "
        "brain organoid cerebral organoid Zika virus neurotropic virus encephalitis; "
        "liver organoid hepatitis malaria Plasmodium liver stage; "
        "macrophage Leishmania intracellular killing assay; "
        "Trypanosoma brucei Trypanosoma cruzi in vitro drug assay high-throughput screening; "
        "Toxoplasma gondii in vitro infection model; "
        "Cryptosporidium intestinal organoid; Giardia cell culture assay; "
        "Plasmodium erythrocyte stage in vitro antimalarial drug screening; "
        "Candida albicans Aspergillus fumigatus Cryptococcus macrophage killing assay; "
        "antifungal MIC EUCAST susceptibility assay; fungal biofilm eradication assay; "
        "gut-on-chip airway-on-chip organ-on-chip bacterial viral infection model; "
        "precision-cut lung slice PCLS ex vivo respiratory infection; "
        "ex vivo human intestinal explant infection."
    ),
)

_SURROGATE_SYSTEM_INJECTION = LLMProposedAlternative(
    three_r_class="replacement",
    method_description=(
        "Reduced-risk surrogate virus and in vitro antimicrobial systems replacing "
        "live-virus animal challenge and in vivo efficacy studies: "
        "pseudovirus lentiviral pseudoparticle VSV pseudotype neutralisation assay "
        "for HIV SARS-CoV-2 Ebola dengue influenza; "
        "replicon system hepatitis C HCV SARS-CoV-2 replicon; "
        "virus-like particle VLP recombinant viral protein binding assay; "
        "minimum inhibitory concentration MIC broth microdilution assay; "
        "time-kill curve antimicrobial assay; biofilm formation eradication assay; "
        "intracellular killing assay macrophage; checkerboard synergy assay; "
        "high-throughput antimicrobial drug screening; "
        "cytokine release TLR innate immune assay PBMC; "
        "complement activation opsonophagocytosis neutrophil killing assay; "
        "ELISPOT vaccine immunogenicity assay; dendritic cell activation in vitro."
    ),
)

_COMPUTATIONAL_INJECTION = LLMProposedAlternative(
    three_r_class="replacement",
    method_description=(
        "Computational and in silico models replacing animal studies in infectious disease "
        "research: molecular docking virtual screening antiviral antibiotic drug-target "
        "interaction viral protease polymerase; "
        "molecular dynamics simulation viral protein spike protein antibiotic ribosome; "
        "machine learning deep learning antimicrobial resistance prediction; "
        "reverse vaccinology in silico vaccine antigen design; "
        "systems biology host-pathogen interaction signalling pathway; "
        "PBPK pharmacokinetic model antibiotic antiviral CNS lung tissue distribution; "
        "SIR SEIR mathematical epidemiological transmission model; "
        "phylogenetic genomic epidemiology pathogen evolution; "
        "single-cell RNA-seq transcriptomics of infected human cells organoids."
    ),
)

_REDUCTION_INJECTION = LLMProposedAlternative(
    three_r_class="reduction",
    method_description=(
        "Lower-organism and reduction strategies replacing mammalian animal infection models: "
        "Galleria mellonella wax moth larva infection model for bacterial fungal antimicrobial "
        "efficacy screening (Staphylococcus aureus MRSA Pseudomonas Candida Aspergillus); "
        "zebrafish larvae infection model for Mycobacterium marinum Staphylococcus Salmonella "
        "Candida Aspergillus antimicrobial drug screening; "
        "C. elegans bacterial infection model for pathogen virulence and drug screening; "
        "Drosophila innate immunity model for host-pathogen genetic screening; "
        "high-throughput in vitro screening to reduce dose-finding animal experiments; "
        "adaptive statistical design for animal infection challenge studies."
    ),
)

# ── Profile ───────────────────────────────────────────────────────────────────

INFECTIOUS_DISEASE_PROFILE = DomainProfile(
    name="infectious_disease",
    vocabulary=INFECTIOUS_DISEASE_VOCABULARY,
    base_path_b=[
        _CELL_ORGANOID_INJECTION,
        _SURROGATE_SYSTEM_INJECTION,
        _COMPUTATIONAL_INJECTION,
        _REDUCTION_INJECTION,
    ],
    base_path_a=[],
    rank_guidance=INFECTIOUS_DISEASE_RANK_GUIDANCE,
)
