"""Ground-truth extraction expectations for the benzophenone reproductive toxicity study."""

from tests.fixtures.ground_truth import ExpectedEvidence, ExpectedExtraction

BENZOPHENONE_REPRODUCTIVE_PROTOCOL = (
    "MATERIALS AND METHODS. Chemical: Benzophenone (BZP) mixed into NIH-07M diet "
    "(99.98% purity). Animals: IGS rats (Crj:CD(SD)IGS) were employed. Acclimatized for "
    "5 days. Housed in breeding rooms at 19.0–25.0 °C and 35.0–75.0% humidity, 12 ventilation "
    "times/hr, 12 hr light cycle. Basal diet and tap water (UV-irradiated) given ad libitum. "
    "Administration to F0 parents started at five weeks old. Dosing: Based on dose-range study "
    "(0, 600, 2000, 6000, 20000 ppm), the definitive highest dose was set at 2000 ppm. "
    "Intermediate and lowest doses were 450 and 100 ppm. Administration period: F0 males treated "
    "for 10+ weeks (pre-mating/mating). F0 females treated through pre-mating, mating, gestation, "
    "and lactation (PND 21). F1 treatment started at 3 weeks old through PND 21 of F2 offspring. "
    "Mating: Females moved to cages of males (1:1 ratio) at age 15 weeks (F0) or 14–15 weeks "
    "(F1). Presence of vaginal plug or sperm defined GD 0. Mating period limited to two weeks. "
    "1. Parental data: Adult rats observed daily for clinical signs. Body weight and food "
    "consumption measured weekly. 1.2) Estrous cycle: Vaginal smears collected daily for two "
    "weeks before mating. 1.3) Sperm examination: Motility measured using sperm auto-analyzer "
    "(HTM-IVOS). Spermatid head counts and morphology examined. 1.4) Serum hormones: Testosterone, "
    "FSH, and LH measured in males; estradiol, FSH, and LH measured in females (RIA method). "
    "1.5) Organ weights: Brain, pituitary, thyroid, liver, kidneys, adrenals, spleen, testes, "
    "epididymides, prostate, seminal vesicles, ovaries, and uterus weighed. 1.6) Pathological "
    "examinations: Histopathology conducted for control and 2000 ppm groups. 2. Litter data: "
    "Pups observed daily. Litter size adjusted to 8 on PND 4. Body weights measured on PND 0, 4, "
    "7, 14, 21. Anogenital distance measured on PND 4. 2.2) Physical development: Pinna "
    "unfolding, incisor eruption, eye opening observed. 2.3) Reflex tests: PND 19 tests for "
    "pain responses, geotaxis, air righting. 2.4) Organ weights at weaning: Brain, thymus, "
    "spleen of one F1/F2 pup per litter. Statistical analyses: Bartlett's method for homogeneity; "
    "one-way ANOVA or Kruskal-Wallis test used. Dunnett's method for inter-group differences. "
    "Significance set at 5%."
)

EXPECTED_BENZOPHENONE_REPRODUCTIVE = ExpectedExtraction(
    study_type_keywords=("two-generation", "reproductive"),
    endpoint_category=None,
    route=["oral"],
    application={"regulatory-use", "basic-research"},
    procedure_keywords=(
        "reproductive",
        "two-generation",
        "two generation",
        "f0",
        "f1",
        "f2",
        "dietary",
        "mating",
        "litter",
        "anogenital",
        "sperm",
    ),
    species="rat",
    animal_counts=None,
    regulatory=None,
    evidence=ExpectedEvidence(
        route="diet",
        species="rat",
    ),
    notes=(
        "Two-generation reproductive toxicity study (OECD TG 416-class) — not represented in "
        "endpoint_category vocabulary. Route is dietary administration (ppm in feed), maps to "
        "'oral'. animal_counts not stated. No OECD TG explicitly cited but multi-generation "
        "design with anogenital distance, sperm analysis, estrous cyclicity, and reproductive "
        "hormones is TG 416-consistent."
    ),
)
