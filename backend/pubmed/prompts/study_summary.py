"""Pre-search summarization prompt.

Extracts three searchable dimensions from a rich study description
(hypothesis + objectives + detailed methods):

  scientific_question  — the core hypothesis / research objective
  endpoint_description — what is measured and how (drives Path A embedding)
  current_method       — what the animal procedure actually does (drives Path B alternatives)
"""

STUDY_SUMMARY_PROMPT = """You are a scientific expert in toxicology and animal research.

Read the study description below and extract three concise, searchable summaries.
These summaries will be used to search a scientific literature database for alternatives
to animal testing. Write them in English regardless of the input language.

STUDY DESCRIPTION:
{study_text}

Return ONLY valid JSON. No preamble. No markdown.

{{
  "scientific_question": "1-2 sentences describing the core hypothesis or research objective.
    What scientific question is this study trying to answer and why?
    Example: 'Determine whether compound X causes acute dermal irritation under regulatory
    conditions required for REACH registration.'",

  "endpoint_description": "2-3 sentences describing the biological endpoint being measured:
    what physiological or biochemical outcome is assessed, which biomarkers or readouts are
    used, and at what timepoints. Write neutrally — do not mention the species or method,
    only the outcome being measured.
    Example: 'Dermal irritation potential assessed by erythema and oedema scoring on
    abraded and intact skin sites at 1, 24, 48 and 72 hours post-exposure. Primary
    endpoint is Mean Irritation Score per OECD TG 404 criteria.'",

  "current_method": "2-3 sentences describing what the animal procedure does: species used,
    how the substance is administered, what is done to the animal, and duration.
    Be specific — this will be used to find alternative methods in the literature.
    Example: 'Wistar rats with shaved dorsal skin receive occlusive patch application of
    the test substance for 4 hours. Skin reactions are scored at multiple timepoints
    post-exposure following OECD TG 404 guidelines. Ten animals per group are used.'"
}}"""


def build_study_summary_prompt(study_text: str) -> str:
    return STUDY_SUMMARY_PROMPT.format(study_text=study_text.strip())
