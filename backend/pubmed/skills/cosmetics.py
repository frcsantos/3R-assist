"""Cosmetics industry safety testing domain profile.

Covers safety testing protocols for cosmetic and personal care products: skin care,
hair products (dyes, bleaches, relaxers), nail products, oral and dental care,
lip products, eye cosmetics, fragrances, UV filters, preservatives, and colourants.

Context: since the EU cosmetics animal testing ban (Regulation 1223/2009), a rich
ecosystem of validated non-animal alternatives exists specifically for cosmetics.
This skill surfaces those methods for protocols in this domain.
"""

from pubmed.models.analysis import LLMProposedAlternative
from pubmed.skills.base import DomainProfile

# ── Vocabulary ────────────────────────────────────────────────────────────────

COSMETICS_VOCABULARY = """KNOWLEDGE BASE VOCABULARY — use these terms where relevant to improve literature retrieval:
- 3Rs / general: "alternative method", "non-animal", "animal-free", "new approach method (NAM)",
  "validated alternative", "cosmetics regulation alternative", "EU cosmetics ban",
  "REACH cosmetics", "OECD test guideline cosmetics"
- Reconstructed human skin (3D) for skin safety: "EpiDerm reconstructed skin",
  "SkinEthic RHE", "Episkin reconstructed epidermis", "MatTek skin model",
  "reconstructed human epidermis", "3D skin model cosmetics",
  "full-thickness skin model EpiDermFT", "skin irritation 3D model"
- In vitro eye safety: "EpiOcular eye irritation", "BCOP bovine corneal opacity permeability",
  "ICE isolated chicken eye test", "HET-CAM hen's egg chorioallantoic membrane",
  "SIRC cell cytotoxicity", "short time exposure STE test", "reconstituted human corneal epithelium",
  "Draize eye replacement", "fluorescein leakage test eye"
- Skin sensitisation alternatives: "h-CLAT human Cell Line Activation Test",
  "KeratinoSens assay", "direct peptide reactivity assay DPRA",
  "U-SENS assay", "IL-8 Luc assay", "SENS-IS assay",
  "genomic allergen rapid detection GARD", "lymph node assay replacement",
  "ARE-Nrf2 luciferase assay", "skin sensitisation adverse outcome pathway"
- Phototoxicity alternatives: "3T3 neutral red uptake phototoxicity test NRU",
  "OECD 432 phototoxicity", "HaCaT phototoxicity assay", "in vitro phototoxicity",
  "reactive oxygen species ROS phototoxicity assay"
- Skin absorption / penetration: "Franz diffusion cell skin penetration",
  "PAMPA skin permeability", "reconstructed skin absorption",
  "OECD TG 428 skin absorption in vitro", "tape stripping skin penetration",
  "ex vivo human skin diffusion", "finite dose skin penetration"
- Hair product safety: "hair follicle organ culture", "hair dye sensitisation in vitro",
  "hair colourant genotoxicity in vitro", "oxidative hair dye Ames test alternative",
  "keratinocyte hair dye assay", "hair bleach irritation cell assay",
  "hair straightener in vitro safety"
- Oral and nail safety: "EpiOral oral mucosa model", "TR146 oral epithelium cell",
  "in vitro oral mucosal irritation", "buccal mucosa model",
  "nail permeability model in vitro", "bovine hoof nail permeability",
  "artificial nail membrane penetration"
- Computational / in silico: "DEREK Nexus cosmetics prediction", "OECD QSAR toolbox cosmetics",
  "Toxtree cosmetics", "in silico skin sensitisation prediction",
  "computational skin penetration model", "QSAR fragrance allergen",
  "in silico phototoxicity prediction", "cosmetics ingredient safety in silico",
  "structure-activity relationship cosmetics", "read-across cosmetics ingredient",
  "threshold of toxicological concern TTC cosmetics"
- Specific ingredient categories: "UV filter safety in vitro", "sunscreen alternative test",
  "fragrance allergen in vitro", "preservative safety assay cosmetics",
  "paraben in vitro", "colorant genotoxicity alternative", "nanomaterial skin penetration",
  "nanoparticle safety in vitro cosmetics\""""

# ── Ranking guidance ──────────────────────────────────────────────────────────

COSMETICS_RANK_GUIDANCE = """
ALWAYS include (cross-cutting for any cosmetics safety protocol):
  - 3D reconstructed human skin assays (EpiDerm, SkinEthic RHE, Episkin) as replacements
    for animal skin irritation or absorption studies
  - In vitro skin sensitisation methods: h-CLAT, KeratinoSens, DPRA, U-SENS, GARD,
    or adverse outcome pathway (AOP)-based approaches
  - In vitro eye irritation replacements: EpiOcular, BCOP, ICE, STE, HET-CAM
  - In vitro phototoxicity: 3T3 NRU phototoxicity test (OECD 432) or newer cell-based assays
  - Computational approaches: QSAR, read-across, DEREK Nexus, TTC for cosmetics ingredient safety
  - Franz diffusion cell or reconstructed skin models for skin penetration/absorption

INCLUDE when relevant to this specific product category or study objective:
  - Hair follicle organ culture or keratinocyte assay for hair dye or bleach protocols
  - EpiOral or TR146 oral mucosa model for oral care (toothpaste, mouthwash, lip) protocols
  - Nail permeability or bovine hoof model for nail product protocols
  - UV filter-specific in vitro phototoxicity or ROS assay for sunscreen protocols
  - Nanomaterial skin penetration assay for cosmetic nanomaterial protocols
  - Fragrance allergen QSAR or in vitro assay for fragrance and perfume protocols
  - Genotoxicity alternatives (Ames test, in vitro micronucleus, HPRT assay) for hair
    dye colourant or preservative protocols

EXCLUDE:
  - Papers reporting in vivo animal Draize eye tests, guinea pig sensitisation studies,
    or animal skin application studies without proposing an alternative or replacement
  - Papers about clinical dermatology, cosmetics consumer perception, or marketing claims
    with no connection to a replaceable safety test

Be strict: a paper must describe or validate a method that replaces, reduces, or refines
animal use in cosmetics safety testing — not merely characterise a cosmetics ingredient
in animals."""

# ── Always-on Path B injections ───────────────────────────────────────────────

_SKIN_EYE_TISSUE_INJECTION = LLMProposedAlternative(
    three_r_class="replacement",
    method_description=(
        "Reconstructed human tissue models replacing animal Draize and skin tests for "
        "cosmetics safety: EpiDerm SkinEthic RHE Episkin reconstructed human epidermis "
        "for skin irritation and corrosion; EpiDermFT full-thickness skin model; "
        "Franz diffusion cell reconstructed skin for skin absorption and penetration "
        "OECD TG 428; EpiOcular reconstituted corneal epithelium for eye irritation; "
        "BCOP bovine corneal opacity permeability test; ICE isolated chicken eye test; "
        "HET-CAM hen's egg chorioallantoic membrane; short time exposure STE assay; "
        "EpiOral TR146 oral mucosa model for oral care product safety; "
        "bovine hoof nail permeability model for nail product safety."
    ),
)

_SENSITISATION_INJECTION = LLMProposedAlternative(
    three_r_class="replacement",
    method_description=(
        "In vitro and in chemico skin sensitisation assays replacing animal guinea pig "
        "or LLNA tests for cosmetics: h-CLAT human cell line activation test; "
        "KeratinoSens ARE-Nrf2 luciferase assay; direct peptide reactivity assay DPRA; "
        "U-SENS assay; IL-8 Luc assay; SENS-IS assay; "
        "genomic allergen rapid detection GARD; "
        "3T3 neutral red uptake phototoxicity NRU OECD 432 for phototoxicity; "
        "HaCaT phototoxicity assay; in vitro ROS reactive oxygen species phototoxicity; "
        "adverse outcome pathway AOP skin sensitisation; "
        "hair dye colourant keratinocyte assay; hair follicle organ culture."
    ),
)

_COMPUTATIONAL_INJECTION = LLMProposedAlternative(
    three_r_class="replacement",
    method_description=(
        "Computational and in silico tools replacing animal safety studies for cosmetics: "
        "QSAR skin sensitisation prediction DEREK Nexus OECD QSAR toolbox; "
        "read-across cosmetics ingredient safety; "
        "threshold of toxicological concern TTC for cosmetics ingredients; "
        "Toxtree Cramer classification for cosmetics; "
        "in silico skin penetration computational model; "
        "QSAR fragrance allergen prediction; "
        "in silico phototoxicity prediction UV filter; "
        "structure-activity relationship SAR cosmetics ingredient; "
        "computational oral mucosa absorption model."
    ),
)

_REDUCTION_INJECTION = LLMProposedAlternative(
    three_r_class="reduction",
    method_description=(
        "Strategies to reduce animal use in cosmetics safety testing: "
        "tiered testing strategy with in vitro and in silico as first tier; "
        "integrated approaches to testing and assessment IATA for cosmetics; "
        "defined approaches DA for skin sensitisation replacing in vivo studies; "
        "weight-of-evidence approach cosmetics ingredient using human data and in vitro; "
        "ex vivo human skin from surgery or skin bank for absorption penetration studies; "
        "in vitro genotoxicity battery Ames test in vitro micronucleus as tier before in vivo."
    ),
)

# ── Profile ───────────────────────────────────────────────────────────────────

COSMETICS_PROFILE = DomainProfile(
    name="cosmetics",
    vocabulary=COSMETICS_VOCABULARY,
    base_path_b=[
        _SKIN_EYE_TISSUE_INJECTION,
        _SENSITISATION_INJECTION,
        _COMPUTATIONAL_INJECTION,
        _REDUCTION_INJECTION,
    ],
    base_path_a=[],
    rank_guidance=COSMETICS_RANK_GUIDANCE,
)
