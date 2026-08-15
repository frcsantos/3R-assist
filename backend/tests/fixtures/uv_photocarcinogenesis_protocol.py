"""Ground-truth extraction expectations for the UV photocarcinogenesis bioassay."""

from tests.fixtures.ground_truth import ExpectedEvidence, ExpectedExtraction

UV_PHOTOCARCINOGENESIS_PROTOCOL = (
    "MATERIALS AND METHODS. Animals and Maintenance: Experiments carried out between "
    "1978–1991. Both male and female hairless albino SKH:HR1 mice were used (6–10 weeks old). "
    "Housed individually with free access to chow and water. Rooms kept at 25 ± 1 °C with yellow "
    "lamps (no UV). Irradiation: Animals received chronic daily UV exposure. Simulated using "
    "6-kW xenon arc and Schott WG320 glass filters (0.64, 1.0, 1.3, 2.0, and 3.0 mm). Daily "
    "UV exposure was adjustable by varying time (120, 85.5, 61.2, or 43.6 min). Irradiation "
    "spectra were zero below 250 nm. Utrecht group used 3 UVA lamps, 5 UVB lamps, and one "
    "germicidal TUV lamp (254 nm). Spreading exposure over a longer period per day increased "
    "carcinogenicity. Tumor Observations: Checked weekly or every other week. Locations mapped "
    "and numbered. Diameters, heights, and characteristics recorded. Detection thresholds set "
    "at 1-, 2-, or 4-mm diameter. Appearance time of 1-mm tumor is t_avg. Corrected for animals "
    "that died without tumors using maximum likelihood method. Inverse relationship between daily "
    "UV exposure and t_50. SD in ln(t) ranged from 0.10–0.18 for UVB and 0.25–0.40 for pure UVA. "
    "Equivalent Dose: Based on reference data from FS40 sunlamp. Equivalent dose E_i calculated "
    "through normalized formula based on t_50. Action Spectrum and Weighted Dose: Integrated "
    "product of irradiation spectrum and action spectrum over wavelengths (250–400 nm). Fit "
    "Procedure: Scaling weighted daily dose to match measured equivalent doses. Philadelphia/"
    "Utrecht match factor expected to be ~0.25. Search for New Action Spectrum: Based on "
    "Lagrange polynomial (Lagrange polynomial of the order n). Polynomial increased in steps of "
    "n until a statistically sound fit was obtained."
)

EXPECTED_UV_PHOTOCARCINOGENESIS = ExpectedExtraction(
    study_type_keywords=("photocarcinogenesis", "uv", "tumor"),
    endpoint_category=None,
    route=None,
    application={"basic-research"},
    procedure_keywords=(
        "uv",
        "photocarcinogen",
        "tumor",
        "irradiation",
        "chronic",
        "action spectrum",
        "carcinogen",
    ),
    species="mouse",
    animal_counts=None,
    regulatory=None,
    evidence=ExpectedEvidence(
        species="SKH",
        procedure_text="uv",
    ),
    notes=(
        "Photocarcinogenesis bioassay (chronic UV-induced skin tumor development) — distinct "
        "from phototoxicity (acute UV cytotoxicity, TG 432). Route is null: UV irradiation is "
        "physical exposure, not a chemical administration route. No test compound administered."
    ),
)
