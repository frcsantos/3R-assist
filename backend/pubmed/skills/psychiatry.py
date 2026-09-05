"""Psychiatric and psychological disease domain profile.

Covers: depression, anxiety disorders, schizophrenia, bipolar disorder, PTSD, OCD,
autism spectrum disorder (ASD), ADHD, addiction and substance use disorders,
eating disorders, and other mental health conditions studied in animal models.
"""

from pubmed.models.analysis import LLMProposedAlternative
from pubmed.skills.base import DomainProfile

# ── Vocabulary ────────────────────────────────────────────────────────────────

PSYCHIATRY_VOCABULARY = """KNOWLEDGE BASE VOCABULARY — use these terms where relevant to improve literature retrieval:
- 3Rs / general: "alternative method", "non-animal", "animal-free", "new approach method (NAM)",
  "replacement method"
- iPSC-derived neural models: "iPSC-derived neurons", "patient-derived iPSC",
  "iPSC cortical neurons", "iPSC GABAergic neurons", "iPSC glutamatergic neurons",
  "iPSC dopaminergic neurons", "iPSC-derived astrocytes", "iPSC-derived microglia",
  "schizophrenia iPSC neurons", "autism ASD iPSC", "bipolar disorder iPSC"
- Brain organoids / 3D neural models: "cortical organoid", "forebrain organoid",
  "cerebral organoid psychiatric", "brain organoid autism schizophrenia",
  "3D neural organoid", "neurosphere psychiatric", "brain-on-chip psychiatric model",
  "organotypic hippocampal slice", "ex vivo brain slice culture"
- Receptor / neurotransmitter assays: "radioligand receptor binding assay",
  "GPCR functional assay", "serotonin receptor assay", "dopamine receptor assay",
  "GABA receptor assay", "glutamate NMDA receptor assay", "synaptosome assay",
  "neurotransmitter release assay", "monoamine oxidase MAO inhibition assay",
  "serotonin transporter SERT assay", "dopamine transporter DAT assay",
  "HTRF receptor assay", "beta-arrestin recruitment assay"
- Synaptic / cellular assays: "synaptic plasticity assay", "LTP LTD in vitro",
  "patch clamp electrophysiology neuron", "calcium imaging neural activity",
  "multielectrode array MEA assay", "dendritic spine morphology assay",
  "synaptogenesis assay", "miniature excitatory postsynaptic current mEPSC"
- Stress / HPA axis in vitro: "glucocorticoid receptor assay", "cortisol HPA in vitro",
  "stress hormone cell model", "CRF corticotropin in vitro assay"
- Computational / in silico: "neural circuit computational model", "computational psychiatry",
  "machine learning psychiatric biomarker", "deep learning EEG fMRI prediction",
  "agent-based social behavior model", "mathematical neurotransmitter dynamics",
  "pharmacokinetic CNS psychiatric drug model", "receptor occupancy model",
  "network analysis brain connectivity", "systems biology monoamine signalling",
  "in silico drug-receptor interaction psychiatric", "connectome computational model"
- Lower organism models: "C. elegans serotonin dopamine", "zebrafish anxiety model",
  "zebrafish depression model", "Drosophila social behavior", "zebrafish addiction model"
- Omics / molecular: "transcriptomics schizophrenia", "single-cell RNA-seq brain psychiatric",
  "GWAS psychiatric disorder", "proteomics synaptic", "epigenomics depression",
  "multi-omics ASD", "whole-exome sequencing psychiatric\""""

# ── Ranking guidance ──────────────────────────────────────────────────────────

PSYCHIATRY_RANK_GUIDANCE = """
ALWAYS include (cross-cutting for any psychiatric or psychological disease protocol):
  - Patient-derived iPSC neurons or brain organoids (cortical, forebrain) from individuals
    with psychiatric diagnoses, as replacements for animal behavioural models
  - In vitro receptor binding and functional assays (serotonin, dopamine, GABA, glutamate,
    noradrenaline) replacing in vivo pharmacological animal experiments
  - Synaptic function assays: patch clamp electrophysiology, MEA, calcium imaging,
    LTP/LTD in vitro, synaptogenesis assay
  - Computational models: neural circuit models, receptor occupancy models, machine learning
    for psychiatric biomarker prediction, pharmacokinetic CNS drug models
  - Ex vivo organotypic brain slice cultures as intermediate alternatives to in vivo recording

INCLUDE when relevant to this specific condition or study objective:
  - Condition-specific iPSC or organoid models (e.g. schizophrenia cortical organoid,
    ASD forebrain organoid, bipolar iPSC neurons)
  - Neurotransmitter system assays matching the protocol's target (e.g. DAT/SERT assay for
    antidepressant or stimulant protocols; GABA receptor assay for anxiety protocols;
    dopamine receptor assay for antipsychotic protocols)
  - C. elegans or zebrafish larvae models used as lower-organism replacements for mammalian
    behavioural paradigms (anxiety, depression, addiction screening)
  - Human neuroimaging data analysis or computational connectome models that replace
    invasive animal electrophysiology or lesion studies
  - Omics approaches on human post-mortem brain tissue or iPSC-derived cells replacing
    animal tissue endpoints

EXCLUDE:
  - Papers reporting results from rodent behavioural models (forced swim test, open field,
    elevated plus maze, sucrose preference, fear conditioning) without proposing an
    alternative or replacement method — animal behavioural study findings are NOT refinements
  - Papers that only characterise a transgenic or lesion animal model without framing it
    as an alternative to a standard paradigm
  - Papers about human clinical psychiatry or psychotherapy with no connection to a
    replaceable animal experiment

Be strict: a paper must describe or validate a method that replaces, reduces, or refines
animal use — not merely study the same psychiatric condition or pathway in animals."""

# ── Always-on Path B injections ───────────────────────────────────────────────

_IPSC_ORGANOID_INJECTION = LLMProposedAlternative(
    three_r_class="replacement",
    method_description=(
        "Patient-derived iPSC neurons and brain organoids as replacements for animal "
        "behavioural models of psychiatric disease: schizophrenia patient iPSC cortical "
        "neurons and forebrain organoids; autism ASD iPSC-derived neurons and brain organoids; "
        "bipolar disorder patient-derived iPSC neurons; depression PTSD neural iPSC models; "
        "iPSC-derived GABAergic glutamatergic dopaminergic neurons; "
        "cortical organoid forebrain organoid for developmental psychiatric disorder modelling; "
        "organotypic hippocampal slice culture; ex vivo brain slice electrophysiology."
    ),
)

_RECEPTOR_ASSAY_INJECTION = LLMProposedAlternative(
    three_r_class="replacement",
    method_description=(
        "In vitro receptor and neurotransmitter assays replacing animal pharmacological models: "
        "radioligand receptor binding assay serotonin dopamine GABA glutamate noradrenaline; "
        "GPCR functional assay beta-arrestin recruitment HTRF FRET; "
        "serotonin transporter SERT dopamine transporter DAT reuptake assay; "
        "monoamine oxidase MAO inhibition assay; "
        "NMDA AMPA glutamate receptor functional assay; "
        "GABA-A chloride flux assay; "
        "synaptosome neurotransmitter release assay; "
        "patch clamp electrophysiology iPSC neurons; "
        "multielectrode array MEA spontaneous neural activity; "
        "calcium imaging synaptic activity; LTP LTD in vitro synaptic plasticity."
    ),
)

_COMPUTATIONAL_INJECTION = LLMProposedAlternative(
    three_r_class="replacement",
    method_description=(
        "Computational and in silico models of psychiatric and psychological conditions "
        "replacing animal behavioural studies: neural circuit computational model of "
        "depression anxiety reward; machine learning deep learning psychiatric biomarker "
        "prediction from EEG fMRI or omics; agent-based model of social behaviour autism; "
        "mathematical model of neurotransmitter dynamics monoamine serotonin dopamine; "
        "pharmacokinetic CNS drug model receptor occupancy prediction; "
        "network analysis brain connectivity connectome psychiatric disorder; "
        "systems biology signalling pathway monoamine stress response; "
        "in silico drug-receptor interaction antidepressant antipsychotic discovery."
    ),
)

_REDUCTION_INJECTION = LLMProposedAlternative(
    three_r_class="reduction",
    method_description=(
        "Strategies to reduce mammalian animal use in psychiatric and psychological research: "
        "C. elegans serotonin dopamine pathway genetic and drug screening; "
        "zebrafish larvae anxiety depression addiction behavioural assay as lower-organism model; "
        "Drosophila social behaviour stress paradigm for genetic screening; "
        "high-throughput in vitro receptor or cell-based drug screening before in vivo; "
        "adaptive statistical design and power calculation for behavioural animal experiments; "
        "in silico pharmacokinetic modelling to reduce dose-ranging animal studies."
    ),
)

# ── Profile ───────────────────────────────────────────────────────────────────

PSYCHIATRY_PROFILE = DomainProfile(
    name="psychiatry_psychology",
    vocabulary=PSYCHIATRY_VOCABULARY,
    base_path_b=[
        _IPSC_ORGANOID_INJECTION,
        _RECEPTOR_ASSAY_INJECTION,
        _COMPUTATIONAL_INJECTION,
        _REDUCTION_INJECTION,
    ],
    base_path_a=[],
    rank_guidance=PSYCHIATRY_RANK_GUIDANCE,
)
