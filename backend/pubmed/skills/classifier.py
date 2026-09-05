"""Classify a protocol into a domain profile.

Classification order:
  1. Detection / contamination signals           → general
  2. Potency-assay signals                       → general
  3. Known toxicology endpoint_category          → toxicology
  4. Toxicology text signals                     → toxicology
  5. Cancer / oncology signals                   → cancer
  6. Neurodegeneration signals                   → neurodegeneration
  7. Psychiatric / psychological signals         → psychiatry
  8. Cardiometabolic signals                     → cardiometabolic
  9. Rare disease / orphan / epigenetic signals  → rare_disease
 10. Autoimmune / autoinflammatory signals       → autoimmune
 11. Consumer product safety signals             → consumer_safety
 12. Infectious disease signals                  → infectious_disease
 13. Cosmetics / personal care signals           → cosmetics
 14. Fallback                                    → general
"""

from __future__ import annotations

from pubmed.skills.autoimmune import AUTOIMMUNE_PROFILE
from pubmed.skills.base import DomainProfile
from pubmed.skills.rare_disease import RARE_DISEASE_PROFILE
from pubmed.skills.cancer import CANCER_PROFILE
from pubmed.skills.cardiometabolic import CARDIOMETABOLIC_PROFILE
from pubmed.skills.consumer_safety import CONSUMER_SAFETY_PROFILE
from pubmed.skills.cosmetics import COSMETICS_PROFILE
from pubmed.skills.infectious_disease import INFECTIOUS_DISEASE_PROFILE
from pubmed.skills.neurodegeneration import NEURODEGENERATION_PROFILE
from pubmed.skills.psychiatry import PSYCHIATRY_PROFILE
from pubmed.skills.toxicology import TOXICOLOGY_PROFILE

# ── General / fallback profile (no injections, minimal vocabulary) ────────────

_GENERAL_VOCABULARY = """KNOWLEDGE BASE VOCABULARY — use these terms where relevant:
- 3Rs / general: "alternative method", "non-animal", "animal-free",
  "new approach method (NAM)", "replacement method"
- In vitro / organotypic: "organoid", "organ-on-a-chip", "microphysiological system",
  "3D cell culture", "spheroid", "iPSC-derived"
- Computational / in silico: "in silico", "QSAR", "read-across", "PBPK",
  "computational model", "machine learning prediction"
- Omics: "transcriptomics", "proteomics", "metabolomics", "pathway analysis\""""

GENERAL_PROFILE = DomainProfile(
    name="general",
    vocabulary=_GENERAL_VOCABULARY,
    rank_guidance=(
        "Include papers that offer evidence to reduce, replace, or refine the "
        "animal use described. Be generous — include borderline papers."
    ),
)

# ── Classifier signals ────────────────────────────────────────────────────────

_DETECTION_SIGNALS = (
    "detection assay", "contamination detection", "sterility test",
    "microbial detection", "pathogen detection", "lethality for detection",
    "bioassay for detection", "bioassay for contamination",
)

_POTENCY_SIGNALS = (
    "potency assay", "in vivo potency", "biological potency",
    "potency determination", "potency testing", "snap-25", "endopeptidase",
    "botulinum potency", "vaccine potency",
)

_TOXICOLOGY_ENDPOINT_CATEGORIES = frozenset({
    "acute_toxicity", "skin_irritation", "skin_corrosion",
    "ocular_irritation", "skin_sensitisation", "phototoxicity",
    "genotoxicity", "pyrogenicity", "skin_absorption",
})

_TOXICOLOGY_TEXT_SIGNALS = (
    "ld50", "dl50", "lethal dose 50", "acute toxicity", "acute lethality",
    "fixed dose procedure", "up-and-down procedure", "acute toxic class",
    "skin irritation", "eye irritation", "skin corrosion",
    "skin sensitisation", "skin sensitization", "genotoxicity", "mutagenicity",
    "phototoxicity", "pyrogenicity", "skin absorption",
    "28-day", "subacute", "repeated dose", "repeated-dose",
    "histopatholog", "organ toxicity",
)

_CANCER_SIGNALS = (
    "cancer", "carcinoma", "sarcoma", "lymphoma", "leukemia", "leukaemia",
    "myeloma", "melanoma", "glioblastoma", "glioma", "neuroblastoma",
    "medulloblastoma", "astrocytoma", "meningioma",
    "tumor", "tumour", "neoplasm", "malignant", "malignancy",
    "metastasis", "metastatic", "oncology", "oncogenesis",
    "xenograft", "orthotopic tumor", "orthotopic tumour",
    "tumor microenvironment", "tumour microenvironment",
    "cancer stem cell", "tumor stem cell", "glioma stem",
    "anticancer", "antitumor", "antitumour", "antineoplastic",
    "tumor angiogenesis", "tumour angiogenesis",
    "tumor invasion", "tumour invasion", "cancer invasion",
    "tumor spheroid", "cancer organoid", "tumoroid",
    "chemotherapy", "immunotherapy",
)

_NEURODEGENERATION_SIGNALS = (
    "alzheimer", "parkinson", "huntington",
    "amyotrophic lateral sclerosis",
    "multiple sclerosis",
    "neurodegeneration", "neurodegenerative",
    "dementia", "frontotemporal dementia", "lewy body dementia",
    "motor neuron disease", "motor neurone disease",
    "spinal muscular atrophy",
    "alpha-synuclein", "synucleinopathy",
    "amyloid beta", "amyloid-beta", "tau phosphorylation", "tau aggregation",
    "neurofibrillary tangle", "senile plaque",
    "huntingtin", "polyglutamine",
    "tdp-43", "dopaminergic neurodegeneration",
    "prion disease",
)

_PSYCHIATRY_SIGNALS = (
    "schizophrenia", "psychosis", "psychotic", "antipsychotic",
    "major depressive disorder", "depressive disorder", "major depression",
    "antidepressant",
    "bipolar disorder", "bipolar affective",
    "anxiety disorder", "generalized anxiety", "social anxiety", "panic disorder",
    "anxiolytic", "anxiogenic",
    "post-traumatic stress", "ptsd",
    "obsessive-compulsive", "ocd",
    "autism spectrum", "autistic", "asperger",
    "attention deficit hyperactivity", "adhd",
    "substance use disorder", "alcohol dependence", "drug dependence", "addiction model",
    "eating disorder", "anorexia nervosa", "bulimia nervosa",
    "psychiatric disorder", "mental disorder", "psychiatric model",
    "serotonin reuptake", "dopamine receptor psychiatric",
    "computational psychiatry", "psychiatric biomarker",
)

_CARDIOMETABOLIC_SIGNALS = (
    "atherosclerosis", "coronary artery disease", "myocardial infarction",
    "heart failure", "cardiomyopathy", "cardiac hypertrophy",
    "arrhythmia", "atrial fibrillation", "ventricular fibrillation",
    "hypertension", "antihypertensive",
    "type 2 diabetes", "type 1 diabetes", "diabetic model", "insulin resistance",
    "metabolic syndrome", "dyslipidemia", "hypercholesterolemia",
    "non-alcoholic fatty liver", "nafld", "nash",
    "cardiovascular disease", "cardiometabolic",
    "cardiac ischaemia", "cardiac ischemia",
    "iPSC-cardiomyocyte", "cardiac organoid", "heart-on-chip",
    "pancreatic beta cell", "islet of langerhans",
    "adipogenesis", "adipocyte differentiation", "obesity model",
)

_CONSUMER_SAFETY_SIGNALS = (
    "food safety", "food additive", "food contaminant", "food allergen",
    "dietary exposure", "dietary ingredient",
    "mycotoxin", "aflatoxin", "ochratoxin", "fumonisin", "deoxynivalenol",
    "pesticide residue", "veterinary drug residue",
    "textile dye", "textile chemical", "fabric safety", "clothing safety",
    "chemical migration", "packaging material safety", "toy safety",
    "consumer product safety", "household product safety",
    "in vitro digestion", "simulated gastrointestinal", "caco-2 food",
    "threshold of toxicological concern", "cramer classification",
    "iso 10993", "biocompatibility material",
)

_RARE_DISEASE_SIGNALS = (
    # explicit rare disease framing
    "rare disease", "rare genetic disorder", "orphan disease", "orphan drug",
    "inborn error of metabolism",
    # lysosomal storage
    "lysosomal storage", "gaucher disease", "fabry disease", "pompe disease",
    "niemann-pick", "mucopolysaccharidosis", "hunter syndrome", "hurler syndrome",
    "krabbe disease", "metachromatic leukodystrophy", "glycogen storage disease",
    # metabolic rare
    "phenylketonuria", "pku", "maple syrup urine disease", "msud",
    "organic aciduria", "fatty acid oxidation disorder", "urea cycle disorder",
    "peroxisomal disorder", "zellweger syndrome",
    # muscular dystrophies
    "duchenne muscular dystrophy", "becker muscular dystrophy",
    "limb-girdle muscular dystrophy", "facioscapulohumeral", "myotonic dystrophy",
    # rare neurological / neurodevelopmental
    "rett syndrome", "fragile x syndrome", "dravet syndrome",
    "tuberous sclerosis", "neurofibromatosis",
    "angelman syndrome", "prader-willi syndrome",
    "spinocerebellar ataxia", "friedreich's ataxia", "friedreich ataxia",
    "beckwith-wiedemann", "digeorge syndrome", "williams syndrome",
    # rare organ disease
    "cystic fibrosis", "cftr mutation",
    "alpha-1 antitrypsin deficiency", "wilson's disease", "alagille syndrome",
    # epigenetic / chromatin disorders
    "kabuki syndrome", "rubinstein-taybi", "coffin-siris",
    "sotos syndrome", "wiedemann-steiner", "imprinting disorder",
    "chromatin remodelling disorder", "dna methylation disorder",
    # gene therapy / orphan drug validation
    "exon skipping", "antisense oligonucleotide rare", "aav gene therapy",
    "enzyme replacement therapy", "substrate reduction therapy",
    "nonsense suppression", "readthrough therapy",
    # connective tissue rare
    "marfan syndrome", "ehlers-danlos syndrome", "osteogenesis imperfecta",
    # other signals
    "cftr organoid", "forskolin swelling assay", "isogenic ipsc control",
)

_AUTOIMMUNE_SIGNALS = (
    "rheumatoid arthritis", "systemic lupus erythematosus", "lupus erythematosus",
    "autoimmune", "autoimmunity",
    "inflammatory bowel disease", "crohn's disease", "crohn disease", "ulcerative colitis",
    "psoriasis", "psoriatic arthritis",
    "sjögren's syndrome", "sjogren's syndrome", "sjogren syndrome",
    "ankylosing spondylitis", "axial spondyloarthritis",
    "hashimoto", "autoimmune thyroiditis", "graves' disease", "graves disease",
    "myasthenia gravis", "systemic sclerosis", "scleroderma",
    "vasculitis", "anca-associated", "giant cell arteritis",
    "pemphigus", "pemphigoid",
    "celiac disease", "coeliac disease",
    "antiphospholipid syndrome",
    "autoimmune hepatitis",
    "dermatomyositis", "polymyositis",
    "fibroblast-like synoviocyte", "collagen-induced arthritis",
    "dss colitis", "tnbs colitis",
    "autoantibody", "anti-citrullinated", "anti-ccp",
    "th17", "treg induction", "regulatory t cell autoimmune",
)

_INFECTIOUS_DISEASE_SIGNALS = (
    # viral
    "viral infection", "virus infection", "antiviral",
    "hiv", "aids", "influenza", "sars-cov-2", "covid-19", "coronavirus",
    "hepatitis b", "hepatitis c", "hepatitis virus",
    "herpes simplex", "herpes virus", "ebola", "dengue", "zika virus",
    "respiratory syncytial virus", "rsv infection", "rabies virus",
    "norovirus", "rotavirus", "cytomegalovirus", "cmv infection",
    "hpv infection", "human papillomavirus",
    # bacterial
    "bacterial infection", "bacteremia", "sepsis model",
    "mycobacterium tuberculosis", "tuberculosis model",
    "staphylococcus aureus", "mrsa", "methicillin-resistant",
    "streptococcus infection", "escherichia coli infection",
    "salmonella infection", "listeria infection",
    "clostridioides difficile", "clostridium difficile",
    "helicobacter pylori", "pseudomonas aeruginosa infection",
    "klebsiella infection", "neisseria infection",
    "antimicrobial resistance", "antibiotic resistance", "antibiotic efficacy",
    # fungal
    "fungal infection", "antifungal", "candida infection", "candida albicans",
    "aspergillus fumigatus", "aspergillosis", "cryptococcus infection",
    "fungal biofilm",
    # parasitic / protozoan
    "malaria", "plasmodium", "leishmania", "trypanosoma", "chagas disease",
    "toxoplasma", "cryptosporidium", "giardia infection",
    "schistosomiasis", "filariasis", "antiparasitic",
    "antimalarial", "trypanocidal",
    # model systems
    "pseudovirus", "replicon system", "virus-like particle infection",
    "minimum inhibitory concentration", "galleria mellonella",
    "infection model animal-free", "organoid infection",
)

_COSMETICS_SIGNALS = (
    "cosmetic ingredient", "cosmetic safety", "cosmetics safety",
    "personal care product", "cosmetics regulation",
    "hair dye", "hair colourant", "hair colorant", "hair bleach",
    "hair relaxer", "hair straightener", "permanent wave",
    "nail polish", "nail product", "nail lacquer",
    "oral care", "toothpaste", "mouthwash", "lip gloss", "lip product",
    "oral mucosa model", "buccal mucosa",
    "fragrance allergen", "perfume allergen", "fragrance sensitisation",
    "uv filter safety", "sunscreen ingredient",
    "preservative cosmetics", "paraben safety",
    "draize test replacement", "cosmetics animal testing ban",
    "epiderm", "skinethic", "episkin",
    "h-clat", "keratinosens", "dpra", "u-sens", "gard assay",
    "epiocular", "bcop assay",
)


def classify_domain(
    protocol_text: str,
    endpoint_category: str | None,
) -> DomainProfile:
    lowered = protocol_text.lower()

    # Detection and potency bioassays use lethality as a readout, not as their
    # endpoint — skip all toxicology injections for these.
    if any(sig in lowered for sig in _DETECTION_SIGNALS):
        return GENERAL_PROFILE
    if any(sig in lowered for sig in _POTENCY_SIGNALS):
        return GENERAL_PROFILE

    # Known toxicology endpoint category → toxicology skill
    if endpoint_category in _TOXICOLOGY_ENDPOINT_CATEGORIES:
        return TOXICOLOGY_PROFILE

    # No structured endpoint but text has clear toxicology signals
    if any(sig in lowered for sig in _TOXICOLOGY_TEXT_SIGNALS):
        return TOXICOLOGY_PROFILE

    # Cancer / oncology protocols
    if any(sig in lowered for sig in _CANCER_SIGNALS):
        return CANCER_PROFILE

    # Neurodegenerative disease protocols
    if any(sig in lowered for sig in _NEURODEGENERATION_SIGNALS):
        return NEURODEGENERATION_PROFILE

    # Psychiatric and psychological disease protocols
    if any(sig in lowered for sig in _PSYCHIATRY_SIGNALS):
        return PSYCHIATRY_PROFILE

    # Cardiometabolic disease protocols
    if any(sig in lowered for sig in _CARDIOMETABOLIC_SIGNALS):
        return CARDIOMETABOLIC_PROFILE

    # Rare diseases, orphan conditions, and epigenetic/genetic disorders
    if any(sig in lowered for sig in _RARE_DISEASE_SIGNALS):
        return RARE_DISEASE_PROFILE

    # Autoimmune and autoinflammatory disease protocols
    if any(sig in lowered for sig in _AUTOIMMUNE_SIGNALS):
        return AUTOIMMUNE_PROFILE

    # Consumer product safety protocols (food, textiles, objects, packaging)
    if any(sig in lowered for sig in _CONSUMER_SAFETY_SIGNALS):
        return CONSUMER_SAFETY_PROFILE

    # Infectious disease protocols (viral, bacterial, fungal, parasitic)
    if any(sig in lowered for sig in _INFECTIOUS_DISEASE_SIGNALS):
        return INFECTIOUS_DISEASE_PROFILE

    # Cosmetics and personal care product safety protocols
    if any(sig in lowered for sig in _COSMETICS_SIGNALS):
        return COSMETICS_PROFILE

    return GENERAL_PROFILE
