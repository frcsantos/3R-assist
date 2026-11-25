"""LLM-based domain classifier prompt.

Asks the LLM to pick the most appropriate domain profile for a protocol.
Used by async_classify_domain() — keyword classifier is the fallback.
"""

DOMAIN_CLASSIFIER_PROMPT = """You are an expert in biomedical research and the 3Rs framework (Replace, Reduce, Refine animal use).

Classify the research protocol below into exactly ONE domain profile.

AVAILABLE PROFILES:
- "toxicology" — regulatory safety toxicology: acute lethality (LD50/LC50), skin or eye
  irritation/corrosion, genotoxicity, sensitisation, phototoxicity, organ toxicity,
  28-day or 90-day repeated-dose studies. The goal is hazard or safety characterisation.
- "cancer" — oncology: tumour growth, metastasis, anticancer drug efficacy, xenograft or
  orthotopic tumour models, cancer immunotherapy, tumour microenvironment.
- "neurodegeneration" — primary neurodegenerative disease as the main focus: Alzheimer's,
  Parkinson's, ALS, Huntington's, frontotemporal dementia, prion disease. Use ONLY when
  neurodegeneration (protein aggregation, neuronal loss) is the primary system being replaced.
- "psychiatry" — psychiatric disorders: schizophrenia, depression, anxiety, autism spectrum
  disorder, ADHD, addiction models, antidepressant or antipsychotic efficacy testing.
- "cardiometabolic" — cardiovascular or metabolic disease: heart failure, atherosclerosis,
  arrhythmia, type 1/2 diabetes, metabolic syndrome, obesity models, NAFLD/NASH.
- "rare_disease" — orphan or rare genetic disease: lysosomal storage disorders, muscular
  dystrophies, cystic fibrosis, rare metabolic conditions, gene therapy for rare disease.
- "autoimmune" — autoimmune or autoinflammatory disease as the PRIMARY clinical focus:
  rheumatoid arthritis, SLE, IBD, psoriasis, myasthenia gravis, Sjögren's. Use when the
  goal is replacing an established disease model (CIA, DSS colitis, EAE as an MS model).
- "consumer_safety" — consumer product safety: food additives, cosmetics ingredients,
  textiles, packaging materials, dietary exposure.
- "infectious_disease" — infection models: viral, bacterial, fungal, or parasitic infections;
  antimicrobial efficacy; pathogen biology.
- "cosmetics" — cosmetics-specific regulatory safety: Draize test replacements, sensitisation
  assays for personal care products, EU cosmetics regulation compliance.
- "basic_science" — mechanistic biology without a specific clinical disease replacement
  target. Includes: signalling pathway studies, cell biology, developmental biology,
  tissue homeostasis, immunological mechanisms (T cell development, thymic selection,
  B cell biology), gene regulation, epigenetics, gene knockout / knockdown / CRISPR
  functional studies, omics (transcriptomics, proteomics, single-cell RNA-seq) used to
  understand biological mechanisms, stem cell biology, any protocol whose primary purpose
  is understanding HOW a biological system works rather than replacing a specific disease model.
  Use this when EAE or another disease readout is used as a validation tool for a mechanistic
  finding, not as the primary system being replaced.
- "general" — does not fit any of the above.

DECISION GUIDE:
- Ask: "Is the primary goal of this protocol to replace or reduce a specific established
  disease model, or to understand a biological mechanism?"
- If mechanism → "basic_science"
- If disease model replacement → pick the matching disease profile
- If regulatory safety endpoint → "toxicology"
- When in doubt between "autoimmune" and "basic_science": choose "basic_science" if the
  protocol is studying how the immune system works (development, selection, regulation)
  rather than replacing a disease model for a specific autoimmune condition.

PROTOCOL:
{protocol_text}

ENDPOINT CATEGORY (structured parameter, may be null): {endpoint_category}

Return ONLY valid JSON. No preamble. No markdown.
{{"domain": "<profile_name>"}}"""


def build_domain_classifier_prompt(
    protocol_text: str,
    endpoint_category: str | None,
) -> str:
    return DOMAIN_CLASSIFIER_PROMPT.format(
        protocol_text=protocol_text.strip(),
        endpoint_category=endpoint_category or "not specified",
    )
