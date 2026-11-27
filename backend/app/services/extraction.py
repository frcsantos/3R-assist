from app.adapters.llm import ExtractionError, LLMAdapter
from app.models.protocol import (
    EvidenceCheck,
    AnalyzeResponse,
    ExperimentResult,
    ExtractionResult,
    RawExtraction,
    to_protocol_parameters,
)
from app.services import article_pipeline, vocabulary
from app.services.language import detect_lang, language_label
from app.services.study_type_lookup import map_study_type_to_endpoint


def _model_endpoint(raw: RawExtraction) -> str | None:
    """The endpoint the model picked from the table, unless it is a root group."""
    if raw.endpoint is None:
        return None
    if vocabulary.endpoint_rows() and not vocabulary.endpoint_ancestors(raw.endpoint):
        return None  # e.g. "human-health-effects" says nothing about the study
    return raw.endpoint


def enrich_raw_extraction(raw: RawExtraction) -> ExtractionResult:
    # The model chooses from the endpoints table; the keyword lookup on study_type
    # only covers what it left empty (or the stub adapter, which never sets it).
    endpoint_category = _model_endpoint(raw) or map_study_type_to_endpoint(raw.study_type)
    return ExtractionResult(raw=raw, endpoint_category=endpoint_category)


def enrich_raw_experiments(raw_list: list[RawExtraction]) -> list[ExtractionResult]:
    return [enrich_raw_extraction(raw) for raw in raw_list]


_EVIDENCE_FIELDS = (
    "route",
    "application",
    "procedure_text",
    "species",
    "animal_counts",
    "regulatory",
    "endpoint",
    "test_system",
    "guideline_ref",
)


def _norm(text: str) -> str:
    return " ".join(text.split())


def verify_evidence(raw: RawExtraction, source_text: str) -> dict[str, EvidenceCheck]:
    """Local check (no LLM call) that each evidence quote really occurs in the source."""
    source = _norm(source_text)
    checks: dict[str, EvidenceCheck] = {}
    for name in _EVIDENCE_FIELDS:
        value = getattr(raw, name)
        evidence = getattr(raw, f"{name}_evidence")
        if value in (None, [], ""):
            continue
        if not evidence:
            if name == "application":
                continue  # coded from a vocabulary; the prompt leaves its evidence null
            checks[name] = EvidenceCheck(status="no_evidence")
            continue
        result = article_pipeline.verify(
            {"value": None, "evidence": _norm(evidence), "status": "found"}, source
        )
        status = "unverified" if result["status"] == "unverified" else "verified"
        if status == "verified" and name == "animal_counts":
            counts = value.model_dump(exclude_none=True)
            if not all(
                article_pipeline.value_in_evidence(n, evidence)
                for n in counts.values()
            ):
                status = "value_not_in_evidence"
        checks[name] = EvidenceCheck(status=status, score=result.get("evidence_score"))
    return checks


def build_analyze_response(
    experiments: list[ExtractionResult],
    *,
    lang: str | None = None,
    source_text: str | None = None,
) -> AnalyzeResponse:
    primary = experiments[0]
    experiment_models = [ExperimentResult.from_extraction(item) for item in experiments]
    if source_text:
        for model in experiment_models:
            model.verification = verify_evidence(model.raw, source_text)
    return AnalyzeResponse(
        experiments=experiment_models,
        params=to_protocol_parameters(primary),
        lang=lang,
    )


class ExtractionService:
    def __init__(self, llm: LLMAdapter) -> None:
        self._llm = llm

    def extract(self, protocol_text: str) -> AnalyzeResponse | ExtractionError:
        lang = detect_lang(protocol_text)
        raw_experiments = self._llm.extract_raw_experiments(
            protocol_text,
            source_language=language_label(lang),
        )
        if isinstance(raw_experiments, ExtractionError):
            return raw_experiments
        experiments = enrich_raw_experiments(raw_experiments)
        if not experiments:
            return ExtractionError()
        return build_analyze_response(experiments, lang=lang, source_text=protocol_text)
