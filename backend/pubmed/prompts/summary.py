"""Prompt for the post-ranking synthesis step.

The LLM receives the ranked recommendations and writes a structured summary.
Citation details (title, authors, year) are resolved from local data after the
LLM returns the PMIDs it cited — so the LLM cannot hallucinate bibliographic fields.
"""

SUMMARY_PROMPT_TEMPLATE = """You are a scientific expert in the 3Rs framework (Replace, Reduce, Refine)
for animal research.

The following ranked list of alternative methods was retrieved from the scientific
literature for the protocol described below. Write a concise synthesis of these findings.

PROTOCOL ENDPOINT: {endpoint_category}
STUDY DOMAIN: {study_domain}
PROCEDURE: {procedure_text}

RANKED ALTERNATIVE METHODS (highest relevance first):
{recommendations_block}

INSTRUCTIONS:
1. Write a synthesis of at most 200 words summarising what the literature offers as
   alternatives for this protocol. Focus on actionable findings.
2. Cite papers inline using [PMID:xxxxxxxx] notation — only cite PMIDs from the list above.
3. Prioritise replacement methods over reduction, and reduction over refinement.
4. If the evidence is weak or limited, say so clearly. Do not overstate findings.
5. Do not invent methods, claims, or citations not present in the list.

Return ONLY valid JSON. No preamble. No markdown.

{{
  "summary": "synthesis text of at most 200 words, with inline [PMID:xxxxxxxx] citations",
  "cited_pmids": ["xxxxxxxx", "yyyyyyyy"]
}}"""


def build_summary_prompt(
    endpoint_category: str | None,
    study_domain: str,
    procedure_text: str | None,
    recommendations: list[dict],
) -> str:
    blocks: list[str] = []
    for rec in recommendations:
        abstract_excerpt = rec["abstract_text"][:300].rstrip()
        if len(rec["abstract_text"]) > 300:
            abstract_excerpt += "..."
        blocks.append(
            f"[{rec['rank']}] PMID:{rec['pmid']} ({rec['three_r_class'].upper()})\n"
            f"Title: {rec['title']}\n"
            f"Abstract: {abstract_excerpt}\n"
            f"Relevance: {rec['relevance_explanation']}"
        )
    return SUMMARY_PROMPT_TEMPLATE.format(
        endpoint_category=endpoint_category or "not specified",
        study_domain=study_domain,
        procedure_text=procedure_text or "not specified",
        recommendations_block="\n\n".join(blocks),
    )
