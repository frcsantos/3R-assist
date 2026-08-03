NECESSITY_PROMPT_TEMPLATE = """You are an expert in the 3Rs framework (Replace, Reduce, Refine) for animal research ethics.

Your task is to assess whether animal use is scientifically necessary for the research protocol below.

Consider:
1. What scientific hypothesis or question is this protocol designed to answer?
2. Can that question be answered using in vitro, ex vivo, computational, or organoid methods?
3. Does the protocol require intact physiology, complex immunology, pharmacokinetics, or behavioral
   endpoints that cannot currently be modelled without a whole animal?
4. Are there validated (OECD, ECVAM, FDA) or emerging alternative methods for the specific
   endpoint category described?

PROTOCOL:
{protocol_text}

EXTRACTED PARAMETERS:
- Endpoint category: {endpoint_category}
- Study domain: {study_domain}
- Species: {species}
- Route of administration: {route}
- Procedure: {procedure_text}
- Regulatory context: {regulatory}

Return ONLY valid JSON. No preamble. No markdown.

{{
  "verdict": "necessary" | "possibly_avoidable" | "not_necessary",
  "confidence": "high" | "medium" | "low",
  "rationale": "2-4 sentences explaining the verdict with scientific reasoning",
  "key_concerns": ["specific scientific or ethical concern 1", "concern 2"],
  "suggested_approach": "If possibly_avoidable or not_necessary, briefly describe a plausible
    non-animal or reduced-animal approach. null if animal use is clearly necessary."
}}

Definitions:
- "necessary"          — the hypothesis requires whole-animal physiology; no validated or
                         emerging alternative can currently answer the question
- "possibly_avoidable" — alternatives exist or are emerging; the protocol should be reviewed
                         against the literature before proceeding with animals
- "not_necessary"      — a validated non-animal method already exists for this endpoint
                         and study domain"""


def build_necessity_prompt(
    protocol_text: str,
    endpoint_category: str | None,
    study_domain: str,
    species: str | None,
    route: list[str] | None,
    procedure_text: str | None,
    regulatory: bool | None,
) -> str:
    return NECESSITY_PROMPT_TEMPLATE.format(
        protocol_text=protocol_text.strip(),
        endpoint_category=endpoint_category or "not specified",
        study_domain=study_domain,
        species=species or "not specified",
        route=", ".join(route) if route else "not specified",
        procedure_text=procedure_text or "not specified",
        regulatory="yes" if regulatory else ("no" if regulatory is False else "not specified"),
    )
