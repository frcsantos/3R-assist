"""Pre-search summarization prompt.

Extracts three searchable dimensions from a rich study description
(hypothesis + objectives + detailed methods):

  scientific_question  — the core hypothesis / research objective
  endpoint_description — what is measured and how (drives Path A embedding)
  current_method       — what the animal procedure actually does (drives Path B alternatives)
"""

STUDY_SUMMARY_PROMPT = """You are a scientific expert in animal research and the 3Rs framework.

Read the study description below and extract three concise, searchable summaries.
These summaries will be used to search a scientific literature database for alternatives
to animal testing. Write them in English regardless of the input language.

CRITICAL: A protocol may contain MULTIPLE distinct animal testing procedures (e.g. an
acute LD50 study AND a 28-day repeated-dose study with organ histology). You MUST
identify and include ALL of them — do not pick only the first or most prominent one.

CRITICAL — DISTINGUISH PURPOSE FROM METHOD: Some protocols use animal lethality as a
readout instrument for a different scientific goal — detecting contamination, determining
biological potency, or titrating a pathogen. In these cases the endpoint is DETECTION or
POTENCY QUANTIFICATION, not toxicity assessment. Do not describe them as "acute toxicity
studies." Example: "Mouse bioassay to detect bacterial contamination by lethality" →
endpoint is "microbial contamination detection", not "acute lethal dose determination".

STUDY DESCRIPTION:
{study_text}

Return ONLY valid JSON. No preamble. No markdown.

{{
  "scientific_question": "1-2 sentences covering ALL research objectives in the protocol.
    If there are multiple animal testing components, mention each.
    Example: 'Determine the acute lethal dose (LD50) and assess subacute organ toxicity
    (liver, kidney, heart, brain histology and blood biochemistry) of compound X in rats.'",

  "endpoint_descriptions": [
    "One entry per distinct animal testing procedure in the protocol. Each entry is 1-2
    sentences describing the scientific PURPOSE of that procedure — what is measured and why.
    Write neutrally, no species names, only scientific objectives.
    If the protocol has only one procedure, return a list with one entry.
    IMPORTANT: if animals are used instrumentally (blood meal sources, tissue donors,
    biological reagent producers), the endpoint is the downstream goal, not welfare monitoring.
    Examples of entries:
      'Acute lethality: single-dose LD50 determination by mortality observation at 24 h
       across a dose range via oral and intraperitoneal routes.'
      'Subacute systemic toxicity: hematological parameters, serum biochemistry (AST, ALT,
       ALP, creatinine, urea, bilirubin), and histopathological examination of liver, kidney,
       heart, brain, spleen, stomach after 28-day repeated oral dosing.'"
  ],

  "current_method": "2-4 sentences describing ALL animal procedures: species, how animals
    are used in each procedure, and what role they play. Be specific — this text is used to
    find alternatives that replace each distinct function.
    If there are multiple procedures, describe each separately.
    IMPORTANT: if animals serve an instrumental role (blood source, tissue donor), describe
    that role clearly.
    Example (multi-procedure): 'Wistar rats receive single oral or intraperitoneal doses
    across dose-range groups; mortality observed 24 h for LD50 determination. Separate groups
    receive daily oral gavage for 28 days; blood drawn on day 28 for haematology and serum
    biochemistry; organs (liver, kidney, heart, brain, spleen, stomach) excised and fixed
    for H&E histopathology on day 29.'"
}}"""


def build_study_summary_prompt(study_text: str) -> str:
    return STUDY_SUMMARY_PROMPT.format(study_text=study_text.strip())
