RANKING_PROMPT_TEMPLATE = """You are an expert in the 3Rs framework for animal research ethics.

A researcher submitted the following protocol. Your task is to evaluate candidate scientific
papers that may offer alternatives, refinements, or reductions to the animal procedure described.

PROTOCOL ENDPOINT: {endpoint_category}
PROTOCOL STUDY DOMAIN: {study_domain}
PROTOCOL PROCEDURE: {procedure_text}

CANDIDATE PAPERS (ordered by semantic similarity):
{candidates_block}

For each paper, determine:
1. Is it relevant to reducing, replacing, or refining the animal use in this protocol?
2. Which 3R class does it best represent? (replacement / reduction / refinement)
3. Does it address the same endpoint_category as the protocol?

Return ONLY valid JSON. No preamble. No markdown.

{{
  "ranked": [
    {{
      "pmid": "the PMID string",
      "relevance_explanation": "1-2 sentences explaining the connection to the protocol endpoint and how it relates to the 3Rs.",
      "three_r_class": "replacement" | "reduction" | "refinement",
      "endpoint_category": one of [acute_toxicity, skin_irritation, skin_corrosion,
        ocular_irritation, skin_sensitisation, phototoxicity, genotoxicity,
        pyrogenicity, skin_absorption] or null,
      "include": true | false
    }}
  ]
}}

Set "include": true when the paper is relevant to the protocol endpoint AND touches on any of:
alternative test methods, in vitro models, computational toxicology, biomarkers,
reduced-animal study designs, or welfare-improving refinements — even if preliminary.
Set "include": false only when the paper is clearly off-topic or has no connection to
the endpoint or to 3Rs principles. Aim to include at least 2-3 papers when possible."""


def build_ranking_prompt(
    endpoint_category: str | None,
    study_domain: str,
    procedure_text: str | None,
    candidates: list[dict],
) -> str:
    blocks: list[str] = []
    for i, c in enumerate(candidates, start=1):
        abstract_excerpt = c["abstract_text"][:400].rstrip()
        if len(c["abstract_text"]) > 400:
            abstract_excerpt += "..."
        blocks.append(
            f"[{i}] PMID:{c['pmid']}\n"
            f"Title: {c['title']}\n"
            f"Abstract: {abstract_excerpt}"
        )
    return RANKING_PROMPT_TEMPLATE.format(
        endpoint_category=endpoint_category or "not specified",
        study_domain=study_domain,
        procedure_text=procedure_text or "not specified",
        candidates_block="\n\n".join(blocks),
    )
