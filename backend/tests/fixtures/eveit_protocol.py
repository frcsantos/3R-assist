"""Ground-truth extraction expectations for the EVEIT ocular irritation protocol."""

from tests.fixtures.ground_truth import ExpectedEvidence, ExpectedExtraction

EVEIT_PROTOCOL = (
    "Materials and Methods. The EVEIT: The EVEIT uses only corneas that are freshly-obtained "
    "from the slaughter house, which involves a delay of up to eight hours prior to preparation "
    "for use. In the development of the method, the eyes were transported in complete heads "
    "cooled to 4 °C. The lids were briefly opened and Polyspectran® eye drops were applied into "
    "the conjunctival sac before transportation. Subsequently, the corneas were excised from the "
    "eyes with a 12mm trephine, and the adhering tissues were gently removed. Each isolated "
    "cornea, with about 2mm of adherent sclera, was placed in a special corneal culture chamber "
    "(ACTO e.V., Aachen, Germany), clamped between the upper and lower parts of the perfusion "
    "chamber. After the placement of the cornea, the chamber was gently filled with perfusion "
    "medium (Minimum Essential Medium [MEM]), with added piperacillin (2mg/ml), amikacin "
    "(0.2mg/ml), and nystatin (400U/ml). The medium was constantly replenished by using a "
    "micropumping system, with an entrance pH of 7.4 ± 0.2 and a flow rate of 6 µl/min. The "
    "chambers were maintained at 32 °C in normal air and 100% relative humidity for 24 hours, "
    "prior to the use of the explanted corneas. Quality control: After stabilisation for "
    "24 hours, the epithelial integrity of the corneas was verified with fluorescein surface "
    "staining (1.7mg/ml fluorescein), an assessment of the endothelial appearance, and the "
    "determination of lactate production. If lactate production was lower than 1mmol/l, or the "
    "epithelium exhibited fluorescein-positive regions, the cornea was excluded. Examination "
    "techniques: The epithelial surface was examined microscopically. The surface was stained "
    "with fluorescein, and images were taken using a Canon EOS 500 digital camera with a "
    "macro-lens. Samples of medium from the artificial anterior chamber outflow were analysed "
    "for glucose, lactate and pH (Bayer Automatic Analyser: Rapid Lab 860). Mechanical "
    "abrasion: A small dental drill (Arkansasschleifer 638XF) was used to create four small "
    "abrasions on the cornea, each with an area of 0.3–0.6 mm². All defects were stained daily "
    "with fluorescein, briefly flushed with isotonic Ringer's solution, and photographed "
    "immediately. Application of test substances: Unpreserved hyaluronate citrate drops "
    "(HYLO-LASOP®) and an artificial tear replacement (physiological saline solution containing "
    "14.581 mmol Ca²⁺ in 0.9% saline) with or without 0.001–0.1% BAC (w/v) were applied exactly "
    "over the apex of the cornea. A 20µl drop of each solution was applied hourly. A soft-tipped "
    "cannula, applying continuous suction, was placed on the lower side of the cornea in culture "
    "to remove excess fluid. Negative controls were represented by two corneas treated with MEM "
    "and artificial tear replacement 24 times per day. A further set of two intact corneas were "
    "used as control for vitality and integrity of the epithelium."
)

EXPECTED_EVEIT = ExpectedExtraction(
    study_type_keywords=("ex vivo", "eye irritation", "eveit", "bovine"),
    endpoint_category="ocular_irritation",
    route=["ocular"],
    application={"basic-research"},
    procedure_keywords=("cornea", "ex vivo", "eveit", "fluorescein", "perfusion", "ocular"),
    species="other",
    animal_counts=None,
    regulatory=None,
    evidence=ExpectedEvidence(
        route="cornea",
        species="slaughter",
        procedure_text=("fluorescein", "cornea", "abrasion", "mechanical"),
    ),
    notes=(
        "EVEIT (Ex Vivo Eye Irritation Test) using post-slaughter bovine corneas — an "
        "alternative to the Draize rabbit eye test. Species is bovine, mapped to 'other'. "
        "animal_counts is null: corneas are slaughterhouse byproducts, not experimental "
        "animals. Returning ocular_irritation recommendations (TG 437/438/460) is correct "
        "behavior."
    ),
)
