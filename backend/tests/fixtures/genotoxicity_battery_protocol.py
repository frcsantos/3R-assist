"""Ground-truth extraction expectations for the estragole/safrole genotoxicity battery."""

from tests.fixtures.ground_truth import ExpectedAnimalCounts, ExpectedEvidence, ExpectedExtraction

GENOTOXICITY_BATTERY_PROTOCOL = (
    "MATERIALS AND METHODS. Test Compound, Dosing Solutions, and Animal Treatment: "
    "Estragole and safrole were purchased from Sigma-Aldrich. Fresh solutions were prepared "
    "in corn oil. Fisher 344 rats were used (housed at 20–24 °C and 55–65% relative humidity, "
    "12-hr light/dark cycle). All rats were fed NIH-31R Purina Rodent Chow and Millipore-filtered "
    "water ad libitum. A three-day treatment protocol was used. Groups of 5 seven-week-old F344 "
    "male rats were treated by gavage with corn oil or with 125, 250, or 450 mg/kg bw safrole, "
    "and with 300, 600, or 1,000 mg/kg bw estragole in corn oil at 0, 24, and 45 hr. Rats were "
    "terminated at 48 hr, 3 hr after the last treatment. Positive controls: 10 mg/kg bw "
    "cyclophosphamide (CP) at 0 and 24 hr and 100 mg/kg bw methyl methanesulfonate (MMS) at "
    "45 hr. Tissue Collection and Storage: Portions of the left lateral lobe of the liver were "
    "removed and washed in cold mincing buffer (HBSS, 20 mM EDTA and 10% DMSO). Liver was minced "
    "to release cells. Glandular stomach was placed in cold mincing buffer on ice for 15 min; "
    "gastric mucosa was rinsed and scraped twice using a scalpel blade to release cells. 100 µl "
    "of blood were collected by cardiac puncture, methanol fixed and stored at -80 °C. Liver and "
    "kidney were fixed in 10% neutral-buffered formalin for histopathology. In Vivo Alkaline Comet "
    "Assay: 100 µl of single cell suspension was mixed with 900 µl 0.8% LMP agarose in PBS at "
    "37 °C; 200 µl was applied to microscope slides. Slides were placed in lysis buffer "
    "(2.5 M NaCl, 0.1 M EDTA, 10 mM Tris, 10% DMSO, 1% Triton X-100) and stored at 4 °C "
    "overnight. Unwinding performed in chilled alkaline solution (300 mM NaOH, 1 mM EDTA, "
    "pH > 13) for 40 min. Electrophoresis performed at 4 °C in the dark for 30 min at "
    "0.7 V/cm and ~300 mA. Slides washed with neutralizing buffer, fixed with ethanol, and "
    "stained with SYBR Gold. Percent DNA in tail was analyzed using Comet IV software. "
    "Enzyme-Modified Alkaline Comet Assay: Performed similarly but with enzyme buffer washes "
    "and application of hOGG1 or Endo III (1:1,000) for 30–45 min at 37 °C before "
    "electrophoresis. Nucleotide Postlabeling: DNA isolated using QIAGEN columns. Isolated DNA "
    "enzymatically digested into 20-deoxyribonucleoside 30-monophosphates. Enriched via nuclease "
    "P1 and labeled using 100 mCi gamma-32P ATP. Resolved using TLC. Micronucleus Assay: "
    "Performed using In Vivo Rat MicroFlow kit (Litron). 100 µl blood fixed with methanol at "
    "-80 °C. Samples resuspend in buffer and analyzed via flow cytometry (anti-CD71 FITC, "
    "anti-CD61 PE, and PI). Histopathology: H&E staining of liver and kidney sections. Lesions "
    "graded for severity from 1 (minimal) to 4 (marked). Statistical Analysis: One-way ANOVA "
    "followed by Dunnett's test; significance set at P < 0.05."
)

EXPECTED_GENOTOXICITY_BATTERY = ExpectedExtraction(
    study_type_keywords=("genotoxicity", "comet", "micronucleus"),
    endpoint_category="genotoxicity",
    route=["oral"],
    application={"regulatory-use", "basic-research"},
    procedure_keywords=(
        "genotox",
        "comet",
        "micronucleus",
        "gavage",
        "estragole",
        "safrole",
        "postlabel",
    ),
    species="rat",
    animal_counts=ExpectedAnimalCounts(per_group=5),
    regulatory=None,
    evidence=ExpectedEvidence(
        route="gavage",
        species=("f344", "344", "fisher"),
        procedure_text=("comet", "gavage", "safrole", "three-day", "treatment protocol"),
    ),
    notes=(
        "Multi-assay genotoxicity battery: alkaline comet (TG 489-class), enzyme-modified comet, "
        "in vivo micronucleus via flow cytometry (TG 474-class), and 32P-postlabeling for DNA "
        "adducts — all sharing one 3-day treatment protocol. animal_counts not stated as a total "
        "(5 per dose group × ~7 groups). Histopathology is ancillary toxicity monitoring."
    ),
)
