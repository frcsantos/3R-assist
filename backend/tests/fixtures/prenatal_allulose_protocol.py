"""Ground-truth extraction expectations for the D-allulose prenatal toxicity study."""

from tests.fixtures.ground_truth import ExpectedAnimalCounts, ExpectedEvidence, ExpectedExtraction

PRENATAL_ALLULOSE_PROTOCOL = (
    "Materials and methods. 2.1. Materials: D-allulose (purity, >98%) was provided by "
    "Samyang Corporation. 2.2. Animals: SD rats (100 females, 60 males) were housed at "
    "22.5–24.5 °C and 53.2–62.8% relative humidity. Quarantined for 8 days. Mating (1:1) "
    "occurred for 5 days. Presence of vaginal plug or sperm defined gestation day 0 (GD0). "
    "All rat maintenance was approved by the Ningbo Institutional Animal Care and Use "
    "Committee, following OECD guidelines 414. 2.3. Study design and parameters: Rats received "
    "either 1250, 2500, 5000 mg/kg bw D-allulose or distilled water on GD6–15 via "
    "intragastric administration (10 mL per kg body weight). Animals observed daily for "
    "mortality, behavioral changes. Weighed once every 3 days. On GD 20, pregnant rats were "
    "weighed, anesthetized, and laparotomized to remove the uteri. Evaluation during caesarean "
    "section was conducted blindly. Endpoints: corpora lutea number, implantation number, "
    "live/dead fetuses, resorption rate. For live fetuses: sex ratio, body weight, body length, "
    "tail length, malformation rates (external, visceral, skeletal). Fetuses fixed in Bouin's "
    "solution (visceral) or 95% ethanol (skeletal). 2.4. Statistical analysis: Data given as "
    "mean ± SD. Kruskal-Wallis ANOVA and Mann-Whitney U test used for non-parametric data; "
    "one-way ANOVA for parametric data. Significance set at p < 0.05."
)

EXPECTED_PRENATAL_ALLULOSE = ExpectedExtraction(
    study_type_keywords=("prenatal", "developmental", "oecd", "414"),
    endpoint_category=None,
    route=["oral"],
    application={"regulatory-use", "basic-research"},
    procedure_keywords=(
        "prenatal",
        "developmental",
        "oecd",
        "414",
        "gavage",
        "intragastric",
        "gd6",
        "fetal",
        "caesarean",
    ),
    species="rat",
    animal_counts=ExpectedAnimalCounts(female=100, male=60, total=160),
    regulatory=True,
    evidence=ExpectedEvidence(
        route="intragastric",
        species=("female", "male", "100", "60", "sd", "rat"),
        regulatory="414",
    ),
    notes=(
        "Prenatal developmental toxicity / embryo-fetal development (OECD TG 414) — not "
        "represented in the endpoint_category vocabulary. 160 total animals (100 females + "
        "60 males); males used for mating only. Effective study subjects are pregnant dams. "
        "Confidence is 'low' per §4.2 (endpoint_category null) despite other fields being "
        "certain."
    ),
)
