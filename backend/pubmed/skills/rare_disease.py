"""Rare disease and rare genetic condition domain profile.

Covers protocols studying orphan / rare diseases, including:
  - Lysosomal storage disorders (Gaucher, Fabry, Pompe, Niemann-Pick, MPS)
  - Inborn errors of metabolism (PKU, MSUD, organic acidurias, glycogen storage diseases)
  - Rare muscular disorders (Duchenne/Becker MD, limb-girdle MD, myotonic dystrophy,
    facioscapulohumeral MD)
  - Rare neurological/neurodevelopmental conditions (Rett syndrome, Fragile X, Dravet
    syndrome, tuberous sclerosis, neurofibromatosis, spinocerebellar ataxias, Friedreich's
    ataxia, rare epilepsies)
  - Chromosomal / copy-number disorders (Down syndrome, DiGeorge/22q11.2, Williams,
    Angelman, Prader-Willi, Beckwith-Wiedemann)
  - Rare connective tissue disorders (Marfan, Ehlers-Danlos, osteogenesis imperfecta)
  - Rare organ diseases (cystic fibrosis, alpha-1 antitrypsin deficiency, Wilson's disease,
    Alagille syndrome, pulmonary arterial hypertension — genetic forms)
  - Epigenetic / chromatin disorders (Rett syndrome MECP2, Kabuki, Rubinstein-Taybi,
    Coffin-Siris, Sotos, Wiedemann-Steiner, imprinting disorders)
  - Orphan drug and gene therapy validation (AAV, ASO, exon skipping, small molecule
    chaperone, enzyme replacement therapy)

Key 3Rs context: patient-derived iPSC models are uniquely powerful here — many rare
disease mutations do not phenocopy in rodents, making animal models poor surrogates,
while patient iPSC-derived cells and organoids capture the exact genetic background.
"""

from pubmed.models.analysis import LLMProposedAlternative
from pubmed.skills.base import DomainProfile

# ── Vocabulary ────────────────────────────────────────────────────────────────

RARE_DISEASE_VOCABULARY = """KNOWLEDGE BASE VOCABULARY — use these terms where relevant to improve literature retrieval:
- 3Rs / general: "alternative method", "non-animal", "animal-free", "new approach method (NAM)",
  "replacement method", "orphan disease model", "patient-derived rare disease model"
- Patient-derived iPSC / gene-edited models: "patient-derived iPSC rare disease",
  "disease-specific iPSC model", "CRISPR-corrected isogenic iPSC control",
  "iPSC-derived neurons rare disease", "iPSC-derived cardiomyocyte rare disease",
  "iPSC-derived hepatocytes rare disease", "iPSC-derived skeletal muscle rare disease",
  "iPSC-derived astrocytes rare disease", "iPSC-derived motor neurons SMA ALS",
  "iPSC patient-specific disease modelling", "CRISPR knock-in rare variant cell model",
  "AAV gene therapy in vitro validation", "antisense oligonucleotide ASO cell assay",
  "exon skipping cell model DMD", "readthrough assay nonsense mutation"
- Lysosomal storage disorders: "enzyme activity assay lysosomal storage disorder",
  "lysosomal enzyme replacement therapy in vitro", "substrate reduction assay cell",
  "glucocerebrosidase GBA assay Gaucher", "alpha-galactosidase assay Fabry disease",
  "acid alpha-glucosidase GAA assay Pompe", "sphingomyelinase assay Niemann-Pick",
  "iduronate sulfatase assay MPS II", "arylsulfatase assay MPS VI",
  "lysosomal biogenesis assay", "autophagy flux assay lysosomal"
- Metabolic rare disease assays: "enzyme activity assay inborn error of metabolism",
  "phenylalanine hydroxylase assay PKU", "branched-chain amino acid assay MSUD",
  "organic acid assay cell model", "fatty acid oxidation assay FAOD",
  "glycogen accumulation assay glycogen storage disease",
  "urea cycle enzyme assay", "peroxisomal function assay"
- Rare muscular disease: "dystrophin expression assay DMD",
  "exon skipping iPSC skeletal muscle DMD", "myotube assay muscular dystrophy",
  "3D skeletal muscle organoid rare disease", "muscle-on-chip DMD model",
  "CRISPR dystrophin correction myotube", "myotonic dystrophy cell model",
  "DM1 MBNL splicing assay", "FSHD D4Z4 chromatin assay"
- Rare neurological / epigenetic: "Rett syndrome MECP2 iPSC neurons",
  "Fragile X FMR1 iPSC neurons", "Dravet syndrome SCN1A iPSC neuron",
  "tuberous sclerosis TSC iPSC organoid", "neurofibromatosis NF1 NF2 cell model",
  "Angelman syndrome UBE3A iPSC", "Prader-Willi imprinting cell model",
  "spinocerebellar ataxia SCA iPSC neuron", "Friedreich's ataxia FXN iPSC",
  "rare epilepsy iPSC neuron model", "MEA multielectrode array rare epilepsy"
- Organoids / 3D models for rare disease: "cystic fibrosis intestinal organoid CFTR",
  "CFTR organoid forskolin swelling assay", "lung organoid cystic fibrosis",
  "liver organoid alpha-1 antitrypsin deficiency Wilson's disease",
  "brain organoid rare neurodevelopmental disorder",
  "kidney organoid rare renal disease", "muscle organoid rare myopathy",
  "cardiac organoid rare cardiomyopathy", "pancreatic organoid rare metabolic"
- Epigenetic assays: "chromatin immunoprecipitation ChIP rare disease",
  "ATAC-seq chromatin accessibility rare disease",
  "DNA methylation analysis imprinting disorder",
  "histone modification assay epigenetic disease",
  "CpG methylation bisulfite sequencing rare disease",
  "Hi-C chromatin conformation rare disease",
  "single-cell ATAC-seq rare disease", "epigenome editing rare disease"
- Computational / in silico: "in silico rare variant interpretation AlphaMissense CADD REVEL",
  "AlphaFold protein structure rare variant", "molecular dynamics rare protein variant",
  "GWAS rare disease susceptibility locus", "whole-exome sequencing rare variant analysis",
  "gene therapy AAV serotype in silico prediction", "off-target prediction CRISPR in silico",
  "machine learning rare disease diagnosis from omics", "patient registry natural history model",
  "pharmacogenomics orphan drug", "systems biology rare disease pathway",
  "RNA splicing prediction rare splice variant", "deep learning variant pathogenicity"
- Lower organism models: "zebrafish rare disease model", "zebrafish morpholino knockdown",
  "zebrafish CRISPR rare gene", "C. elegans rare gene function model",
  "Drosophila rare disease gene model", "yeast complementation assay rare variant",
  "yeast two-hybrid rare protein interaction\""""

# ── Ranking guidance ──────────────────────────────────────────────────────────

RARE_DISEASE_RANK_GUIDANCE = """
ALWAYS include (cross-cutting for any rare disease or orphan condition protocol):
  - Patient-derived iPSC models carrying the specific disease mutation, especially when no
    faithful animal model exists — these are the primary replacement for rare disease
    animal studies given the poor genetic translatability
  - CRISPR-corrected isogenic iPSC controls that isolate the causal variant effect
  - Organoids derived from patient cells (intestinal, liver, brain, kidney, cardiac, muscle)
    as disease-specific replacements for animal organ endpoints
  - In vitro gene therapy validation assays: AAV transduction efficiency in patient-derived
    cells, ASO exon-skipping or splicing correction, readthrough of nonsense mutations
  - Computational rare variant interpretation: AlphaFold, AlphaMissense, CADD, REVEL,
    molecular dynamics of mutant proteins

INCLUDE when relevant to this specific disease category or study objective:
  - Enzyme activity or substrate reduction assays for lysosomal storage disorder or
    inborn error of metabolism protocols (replacing enzyme correction studies in mice)
  - CFTR organoid forskolin swelling assay for cystic fibrosis protocols (clinically
    validated replacement for animal lung endpoints)
  - Dystrophin expression, exon-skipping, or 3D myotube/muscle organoid assay for
    muscular dystrophy protocols
  - iPSC-derived neurons with MEA or calcium imaging for rare epilepsy or
    neurodevelopmental condition protocols
  - Epigenetic assays (ChIP-seq, ATAC-seq, DNA methylation bisulfite, Hi-C) on patient
    cells or corrected iPSC lines for imprinting or chromatin disorder protocols
  - Whole-exome or whole-genome sequencing with computational variant classification
    replacing in vivo phenotype characterisation in knock-in mouse models
  - Zebrafish, C. elegans, or Drosophila carrying orthologous gene knockdown/knockout as
    lower-organism reduction alternatives before mammalian studies
  - Patient registry data modelling or natural history computational models reducing
    the need for chronic animal disease progression studies

EXCLUDE:
  - Papers that only characterise a knock-in or transgenic animal model of a rare disease
    without proposing an alternative, replacement, or reduction strategy
  - Papers about clinical genetic counselling, newborn screening, or patient diagnosis
    with no connection to a replaceable animal experiment

Be strict: a paper must describe or validate a method that replaces, reduces, or refines
animal use in rare disease research — not merely characterise disease biology or a
therapeutic target in an animal model."""

# ── Always-on Path B injections ───────────────────────────────────────────────

_IPSC_GENE_EDIT_INJECTION = LLMProposedAlternative(
    three_r_class="replacement",
    method_description=(
        "Patient-derived iPSC and gene-edited cell models replacing animal rare disease models: "
        "disease-specific iPSC carrying patient mutation differentiated to relevant cell type "
        "— neurons (Rett Fragile X Dravet spinocerebellar ataxia Friedreich's ataxia "
        "rare epilepsy), cardiomyocytes (rare cardiomyopathy), hepatocytes (Wilson's disease "
        "alpha-1 antitrypsin deficiency), skeletal myotubes (Duchenne Becker muscular dystrophy "
        "limb-girdle myotonic dystrophy); "
        "CRISPR-corrected isogenic iPSC control for causal variant validation; "
        "CRISPR knock-in rare disease variant in human cell line; "
        "AAV gene therapy transduction efficiency assay patient-derived cells; "
        "antisense oligonucleotide ASO correction in patient cells; "
        "exon skipping assay DMD dystrophin restoration; "
        "readthrough assay PTC124 ataluren nonsense mutation correction."
    ),
)

_ORGANOID_ENZYME_INJECTION = LLMProposedAlternative(
    three_r_class="replacement",
    method_description=(
        "Organoid and biochemical assays replacing animal organ endpoints in rare disease: "
        "CFTR intestinal organoid forskolin swelling assay for cystic fibrosis "
        "drug and gene therapy validation; "
        "lung organoid cystic fibrosis CFTR; "
        "liver organoid for alpha-1 antitrypsin deficiency Wilson's disease Alagille syndrome; "
        "brain organoid for rare neurodevelopmental disorders tuberous sclerosis "
        "neurofibromatosis Down syndrome DiGeorge Angelman Prader-Willi; "
        "3D skeletal muscle organoid muscle-on-chip for muscular dystrophy; "
        "kidney organoid for rare renal genetic disease; "
        "enzyme activity assay lysosomal storage disorder Gaucher GBA Fabry GLA "
        "Pompe GAA Niemann-Pick sphingomyelinase MPS iduronate sulfatase arylsulfatase; "
        "substrate reduction assay cell model lysosomal; "
        "fatty acid oxidation assay glycogen accumulation assay metabolic rare disease."
    ),
)

_COMPUTATIONAL_INJECTION = LLMProposedAlternative(
    three_r_class="replacement",
    method_description=(
        "Computational and in silico tools replacing animal studies in rare disease research: "
        "AlphaFold protein structure prediction for rare missense variants; "
        "AlphaMissense CADD REVEL SpliceAI in silico pathogenicity scoring for rare variants; "
        "molecular dynamics simulation of rare protein variant functional impact; "
        "whole-exome whole-genome sequencing computational variant classification pipeline; "
        "machine learning deep learning rare disease diagnosis from multi-omics; "
        "off-target prediction CRISPR gene therapy in silico; "
        "AAV capsid serotype tropism in silico prediction; "
        "RNA splicing prediction for rare splice-site variants; "
        "pharmacogenomics model orphan drug candidate prioritisation; "
        "systems biology pathway model rare metabolic disease; "
        "natural history computational model patient registry data."
    ),
)

_REDUCTION_INJECTION = LLMProposedAlternative(
    three_r_class="reduction",
    method_description=(
        "Lower-organism and reduction strategies for rare disease research: "
        "zebrafish larvae CRISPR morpholino knockdown model of rare gene for "
        "phenotype characterisation and drug screening before mammalian studies; "
        "C. elegans knockdown model for rare gene function and drug screening; "
        "Drosophila rare disease gene model for genetic modifier and drug screening; "
        "yeast complementation assay for rare missense variant functional validation; "
        "yeast two-hybrid assay for rare protein-protein interaction; "
        "epigenetic assays on patient blood or fibroblasts as non-invasive endpoint "
        "replacing animal tissue — ChIP-seq ATAC-seq DNA methylation bisulfite sequencing "
        "histone modification Hi-C chromatin conformation for imprinting and epigenetic disorders."
    ),
)

# ── Profile ───────────────────────────────────────────────────────────────────

RARE_DISEASE_PROFILE = DomainProfile(
    name="rare_disease",
    vocabulary=RARE_DISEASE_VOCABULARY,
    base_path_b=[
        _IPSC_GENE_EDIT_INJECTION,
        _ORGANOID_ENZYME_INJECTION,
        _COMPUTATIONAL_INJECTION,
        _REDUCTION_INJECTION,
    ],
    base_path_a=[],
    rank_guidance=RARE_DISEASE_RANK_GUIDANCE,
)
