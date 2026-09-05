"""Consumer product safety testing domain profile.

Covers protocols that test the safety of consumer products for regulatory approval:
food additives and contaminants, food allergens, dietary ingredients, textiles and
clothing dyes/finishes, household objects, toys, packaging materials, and cosmetics
that fall outside the standard toxicology-endpoint regulatory tests (skin irritation,
sensitisation, etc. are already handled by the toxicology skill).

Key 3Rs context: many product safety tests historically relied on animal ingestion or
dermal studies; validated alternatives now include in vitro digestion/absorption models,
reconstructed human skin and intestine, and computational read-across for chemical
migration from materials.
"""

from pubmed.models.analysis import LLMProposedAlternative
from pubmed.skills.base import DomainProfile

# ── Vocabulary ────────────────────────────────────────────────────────────────

CONSUMER_SAFETY_VOCABULARY = """KNOWLEDGE BASE VOCABULARY — use these terms where relevant to improve literature retrieval:
- 3Rs / general: "alternative method", "non-animal", "animal-free", "new approach method (NAM)",
  "replacement method", "validated alternative", "OECD test guideline alternative"
- Food safety / oral exposure models: "in vitro digestion model", "INFOGEST digestion protocol",
  "TIM gastrointestinal model", "simulated gastrointestinal digestion",
  "Caco-2 intestinal absorption", "PAMPA oral bioavailability", "intestinal permeability assay",
  "gut organoid food safety", "intestinal epithelial cell model", "3D gut model",
  "in vitro bioaccessibility assay", "food contaminant bioavailability assay"
- Food allergen / mycotoxin in vitro: "mycotoxin cytotoxicity assay", "aflatoxin in vitro",
  "ochratoxin cell assay", "fumonisin in vitro model", "food allergen cell-based assay",
  "allergen IgE binding in vitro", "BASO activation test food allergen",
  "intestinal permeability allergen", "food processing Maillard reaction in vitro"
- Textile / clothing / material safety: "in vitro skin sensitisation textile dye",
  "h-CLAT assay clothing dye", "KeratinoSens assay textile chemical",
  "DPRA direct peptide reactivity assay", "chemical migration from textile in vitro",
  "eluate cytotoxicity assay material", "ISO 10993 in vitro biocompatibility",
  "Caco-2 chemical migration packaging", "reconstructed skin textile contact"
- Reconstructed human tissue for product safety: "EpiDerm skin irritation",
  "SkinEthic RHE reconstructed epidermis", "EpiOcular eye irritation test",
  "MatTek reconstructed tissue", "3D reconstructed skin product safety",
  "Episkin reconstructed epidermis", "reconstituted human corneal epithelium"
- Computational / in silico: "read-across food safety", "QSAR food contaminant",
  "in silico dietary exposure assessment", "Cramer classification food additive",
  "threshold of toxicological concern TTC", "chemical migration in silico model",
  "computational food allergen cross-reactivity", "PBPK dietary exposure",
  "structure-activity relationship food chemical", "in silico toxicology food additive"
- Lower organism models: "C. elegans food toxicity assay", "zebrafish food contaminant",
  "zebrafish toxicity screening food", "Drosophila dietary toxicity"
- Omics / mechanistic: "transcriptomics food contaminant", "pathway analysis food safety",
  "metabolomics dietary exposure", "proteomics gut food toxicity",
  "adverse outcome pathway food safety", "AOP food allergy\""""

# ── Ranking guidance ──────────────────────────────────────────────────────────

CONSUMER_SAFETY_RANK_GUIDANCE = """
ALWAYS include (cross-cutting for any consumer product safety protocol):
  - In vitro digestion and intestinal absorption models (INFOGEST, Caco-2, gut organoids)
    as replacements for gavage or dietary animal studies
  - Reconstructed human skin or corneal epithelium assays (EpiDerm, SkinEthic, EpiOcular)
    for topical product safety
  - Computational read-across, QSAR, threshold of toxicological concern (TTC), or
    Cramer classification as replacements for animal chemical safety studies
  - Adverse outcome pathway (AOP) frameworks applied to food or material safety

INCLUDE when relevant to this specific product or study objective:
  - Allergen-specific in vitro assays (IgE binding, basophil activation, intestinal
    permeability) for food allergen protocols
  - Mycotoxin or food contaminant cytotoxicity assay for food safety protocols
  - In vitro skin sensitisation assays (h-CLAT, KeratinoSens, DPRA) for textile/material
    chemicals causing skin contact allergy
  - ISO 10993 in vitro biocompatibility assays for toys or household objects
  - Chemical migration in silico or in vitro models for packaging or textile safety
  - In vitro oral bioavailability model for dietary ingredient or food additive protocols
  - Zebrafish or C. elegans as lower-organism reduction intermediates for food toxicant screening
  - Omics or AOP approaches on human cells or patient samples replacing animal endpoints

EXCLUDE:
  - Papers reporting in vivo animal feeding studies, dermal animal studies, or rodent
    inhalation studies without proposing an alternative or replacement method
  - Papers about clinical food allergy diagnosis or consumer epidemiology with no connection
    to a replaceable animal experiment

Be strict: a paper must describe or validate a method that replaces, reduces, or refines
animal use — not merely study the same food chemical or material in animals."""

# ── Always-on Path B injections ───────────────────────────────────────────────

_ORAL_ABSORPTION_INJECTION = LLMProposedAlternative(
    three_r_class="replacement",
    method_description=(
        "In vitro oral exposure, digestion and absorption models replacing animal gavage "
        "and dietary studies for food and ingredient safety: INFOGEST simulated "
        "gastrointestinal digestion protocol; TIM gastrointestinal model; "
        "Caco-2 intestinal absorption and permeability assay; PAMPA oral bioavailability; "
        "gut organoid intestinal epithelial model food safety; "
        "in vitro bioaccessibility assay food contaminant; "
        "mycotoxin aflatoxin ochratoxin fumonisin cytotoxicity in vitro assay; "
        "food allergen IgE binding basophil activation test in vitro."
    ),
)

_SKIN_TISSUE_INJECTION = LLMProposedAlternative(
    three_r_class="replacement",
    method_description=(
        "Reconstructed human tissue and cell-based assays replacing animal dermal studies "
        "for consumer product safety: EpiDerm SkinEthic Episkin reconstructed human "
        "epidermis for skin irritation; EpiOcular reconstituted corneal epithelium "
        "for eye irritation; h-CLAT KeratinoSens direct peptide reactivity assay DPRA "
        "for skin sensitisation from textile dyes or clothing chemicals; "
        "ISO 10993 in vitro biocompatibility assay for toys and household objects; "
        "eluate cytotoxicity assay for material extracts; "
        "chemical migration Caco-2 packaging textile in vitro."
    ),
)

_COMPUTATIONAL_INJECTION = LLMProposedAlternative(
    three_r_class="replacement",
    method_description=(
        "Computational and in silico tools replacing animal safety studies for consumer "
        "products: QSAR read-across for food additive contaminant toxicity prediction; "
        "threshold of toxicological concern TTC approach for food chemicals; "
        "Cramer classification scheme for food ingredient safety; "
        "in silico dietary exposure and PBPK model for food additive bioavailability; "
        "chemical migration in silico model for packaging or textile materials; "
        "adverse outcome pathway AOP for food allergy or skin sensitisation; "
        "computational food allergen cross-reactivity prediction; "
        "structure-activity relationship SAR food chemical safety."
    ),
)

_REDUCTION_INJECTION = LLMProposedAlternative(
    three_r_class="reduction",
    method_description=(
        "Strategies to reduce mammalian animal use in consumer product safety testing: "
        "zebrafish larvae for food contaminant or packaging chemical toxicity screening; "
        "C. elegans for food toxicant or dietary ingredient screening; "
        "Drosophila for dietary toxicity genetic screening; "
        "high-throughput in vitro cell assay for ranking candidates before in vivo; "
        "tiered testing strategy with in vitro and in silico as first tier to reduce animal use; "
        "adaptive or sequential statistical design for animal dose studies."
    ),
)

# ── Profile ───────────────────────────────────────────────────────────────────

CONSUMER_SAFETY_PROFILE = DomainProfile(
    name="consumer_product_safety",
    vocabulary=CONSUMER_SAFETY_VOCABULARY,
    base_path_b=[
        _ORAL_ABSORPTION_INJECTION,
        _SKIN_TISSUE_INJECTION,
        _COMPUTATIONAL_INJECTION,
        _REDUCTION_INJECTION,
    ],
    base_path_a=[],
    rank_guidance=CONSUMER_SAFETY_RANK_GUIDANCE,
)
