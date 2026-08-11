"""Map LLM study_type strings to controlled endpoint_category values.

Lookup table owned by docs/parameter_model.md §4.1.
"""

from __future__ import annotations

from app.models.protocol import EndpointCategory

# study_type strings containing these must not map to acute_toxicity — "subacute"
# contains the substring "acute toxicity" (§4.1 known miss).
_ACUTE_TOXICITY_BLOCKLIST = (
    "subacute",
    "sub-acute",
    "subchronic",
    "sub-chronic",
    "repeated-dose",
    "repeated dose",
    "repeat-dose",
    "28-day",
    "90-day",
    "chronic toxicity",
    "subchronic toxicity",
)

STUDY_TYPE_LOOKUP: list[tuple[tuple[str, ...], EndpointCategory]] = [
    (
        (
            "acute toxicity",
            "ld50",
            "dl50",
            "lethal dose",
            "acute lethality",
            "fixed dose procedure",
            "acute toxic class",
            "up-and-down procedure",
        ),
        "acute_toxicity",
    ),
    (
        ("skin irritation", "dermal irritation", "primary skin irritation"),
        "skin_irritation",
    ),
    (
        ("skin corrosion", "dermal corrosion", "corrosivity"),
        "skin_corrosion",
    ),
    (
        (
            "ocular irritation",
            "eye irritation",
            "draize eye",
            "corneal irritation",
            "conjunctival",
            "eveit",
            "ex vivo eye",
            "bcop",
        ),
        "ocular_irritation",
    ),
    (
        (
            "skin sensitisation",
            "skin sensitization",
            "contact sensitisation",
            "allergic contact",
            "llna",
            "local lymph node",
        ),
        "skin_sensitisation",
    ),
    (
        ("phototoxicity", "photoirritation", "3t3 nru", "photosensitization"),
        "phototoxicity",
    ),
    (
        (
            "genotoxicity",
            "mutagenicity",
            "clastogenicity",
            "chromosomal aberration",
            "ames",
            "bacterial reverse mutation",
            "micronucleus",
            "comet assay",
            "dna strand break",
            "hprt",
            "gene mutation",
        ),
        "genotoxicity",
    ),
    (
        (
            "skin absorption",
            "dermal absorption",
            "percutaneous absorption",
            "skin penetration",
        ),
        "skin_absorption",
    ),
    (
        (
            "reproductive toxicity",
            "developmental toxicity",
            "reproductive and developmental",
            "prenatal developmental",
            "two-generation reproductive",
            "two generation reproductive",
            "fertility",
            "teratogenicity",
            "embryo-fetal",
            "embryofetal",
            "combined screening",
        ),
        "reproductive_toxicity",
    ),
    (
        (
            "endocrine activity",
            "endocrine disruption",
            "estrogenic",
            "androgenic",
            "steroidogenic",
            "estrogen receptor",
            "androgen receptor",
        ),
        "endocrine_activity",
    ),
    (
        (
            "photoreactivity",
            "photoreactive",
            "reactive oxygen species",
            "ros generation",
        ),
        "photoreactivity",
    ),
    (
        (
            "aquatic toxicity",
            "fish embryo",
            "fish early life",
            "fetax",
            "daphnia",
            "algae growth",
        ),
        "aquatic_toxicity",
    ),
    (
        (
            "toxicokinetics",
            "toxicokinetic",
            "adme",
            "intrinsic clearance",
            "metabolic clearance",
            "hepatic clearance",
        ),
        "toxicokinetics",
    ),
    (
        (
            "bacterial endotoxin",
            "endotoxin test",
            "endotoxin activity",
            "bacterial endotoxins",
            "lal test",
            "lal assay",
            "lal",
            "bet assay",
            "limulus amebocyte",
            "limulus amoebocyte",
        ),
        "bacterial_endotoxin",
    ),
    (
        (
            "pyrogenicity",
            "pyrogen",
            "monocyte activation",
            "mat assay",
            "rabbit pyrogen",
        ),
        "pyrogenicity",
    ),
    (
        (
            "rabies diagnosis",
            "rabies virus",
            "rabies antigen",
            "rabies detection",
        ),
        "rabies_diagnosis",
    ),
]


def map_study_type_to_endpoint(study_type: str) -> EndpointCategory | None:
    lowered = study_type.lower()
    for keywords, endpoint in STUDY_TYPE_LOOKUP:
        if endpoint == "acute_toxicity" and any(
            block in lowered for block in _ACUTE_TOXICITY_BLOCKLIST
        ):
            continue
        if any(keyword in lowered for keyword in keywords):
            return endpoint
    return None
