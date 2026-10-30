"""Weighted field-level scoring for extraction reliability benchmarks."""

from __future__ import annotations

from dataclasses import dataclass, field

from app.adapters.llm import ExtractionError
from app.models.protocol import (
    AnimalCounts,
    ExtractionResult,
    RawExtraction,
    normalize_endpoint_slug,
)
from tests.fixtures.ground_truth import (
    ExpectedAnimalCounts,
    ExpectedExtraction,
    ExpectedSplitting,
)

FIELD_WEIGHTS: dict[str, float] = {
    "endpoint_category": 0.30,
    "route": 0.15,
    "species": 0.15,
    "animal_counts": 0.15,
    "regulatory": 0.10,
    "splitting_experiments": 0.15,
}


@dataclass(frozen=True)
class FieldScores:
    endpoint_category: float
    route: float
    species: float
    animal_counts: float
    regulatory: float
    splitting_experiments: float

    @property
    def weighted_total(self) -> float:
        return sum(FIELD_WEIGHTS[name] * getattr(self, name) for name in FIELD_WEIGHTS)

    def as_dict(self) -> dict[str, float]:
        return {name: getattr(self, name) for name in FIELD_WEIGHTS}


@dataclass
class CaseScore:
    case_name: str
    model: str
    field_scores: FieldScores
    extraction_error: str | None = None
    experiment_count: int | None = None

    @property
    def weighted_total(self) -> float:
        return self.field_scores.weighted_total


@dataclass
class PerformanceReport:
    model: str
    case_scores: list[CaseScore] = field(default_factory=list)

    @property
    def overall_score(self) -> float:
        if not self.case_scores:
            return 0.0
        return sum(case.weighted_total for case in self.case_scores) / len(self.case_scores)

    def field_averages(self) -> dict[str, float]:
        if not self.case_scores:
            return {name: 0.0 for name in FIELD_WEIGHTS}
        totals = {name: 0.0 for name in FIELD_WEIGHTS}
        for case in self.case_scores:
            for name, value in case.field_scores.as_dict().items():
                totals[name] += value
        count = len(self.case_scores)
        return {name: totals[name] / count for name in FIELD_WEIGHTS}

    def weighted_field_contributions(self) -> dict[str, float]:
        averages = self.field_averages()
        return {
            name: averages[name] * FIELD_WEIGHTS[name] for name in FIELD_WEIGHTS
        }


_SESSION_SCORES: list[CaseScore] = []


def reset_session_scores() -> None:
    _SESSION_SCORES.clear()


def record_case_score(case_score: CaseScore) -> None:
    _SESSION_SCORES.append(case_score)


def get_session_scores() -> list[CaseScore]:
    return list(_SESSION_SCORES)


def build_performance_report(model: str) -> PerformanceReport:
    return PerformanceReport(
        model=model,
        case_scores=[case for case in _SESSION_SCORES if case.model == model],
    )


def score_endpoint_category(result: ExtractionResult, expected: ExpectedExtraction) -> float:
    # 'acute_toxicity' (keyword lookup) and 'acute-systemic-toxicity' (model, table slug)
    # are the same endpoint; compare them in their normalized form.
    return (
        1.0
        if normalize_endpoint_slug(result.endpoint_category)
        == normalize_endpoint_slug(expected.endpoint_category)
        else 0.0
    )


def score_route(
    result: ExtractionResult,
    expected: ExpectedExtraction,
    *,
    strict_routes: bool = True,
) -> float:
    raw = result.raw
    if expected.route is not None:
        got_routes = set(raw.route or [])
        want_routes = set(expected.route)
        if not want_routes.issubset(got_routes):
            return 0.0
        if strict_routes and got_routes != want_routes:
            return 0.0
        return 1.0
    return 1.0 if not raw.route else 0.0


def score_species(result: ExtractionResult, expected: ExpectedExtraction) -> float:
    return 1.0 if result.raw.species == expected.species else 0.0


def is_empty_animal_counts(counts: AnimalCounts | None) -> bool:
    if counts is None:
        return True
    return all(
        getattr(counts, field_name) is None
        for field_name in ("female", "male", "total", "per_group")
    )


def normalize_animal_counts(counts: AnimalCounts | None) -> AnimalCounts | None:
    if is_empty_animal_counts(counts):
        return None
    return counts


def effective_animal_total(counts: AnimalCounts) -> int | None:
    if counts.total is not None:
        return counts.total
    if counts.female is not None and counts.male is not None:
        return counts.female + counts.male
    return None


def animal_counts_match(
    got: AnimalCounts | None,
    expected: ExpectedAnimalCounts | None,
) -> bool:
    got = normalize_animal_counts(got)
    if expected is None:
        return got is None
    if got is None:
        return False

    for field_name in ("female", "male", "per_group"):
        expected_value = getattr(expected, field_name)
        if expected_value is not None and getattr(got, field_name) != expected_value:
            return False

    if expected.total is not None:
        return effective_animal_total(got) == expected.total
    return True


def score_animal_counts(result: ExtractionResult, expected: ExpectedExtraction) -> float:
    return 1.0 if animal_counts_match(result.raw.animal_counts, expected.animal_counts) else 0.0


def score_regulatory(result: ExtractionResult, expected: ExpectedExtraction) -> float:
    if expected.regulatory is None:
        return 1.0
    return 1.0 if result.raw.regulatory == expected.regulatory else 0.0


def score_splitting_experiments(
    results: list[ExtractionResult] | ExtractionError,
    splitting: ExpectedSplitting,
) -> float:
    if isinstance(results, ExtractionError):
        return 0.0
    count = len(results)
    if count < splitting.min_count:
        return 0.0
    if splitting.max_count is not None and count > splitting.max_count:
        return 0.0
    if splitting.primary_index >= count:
        return 0.0
    return 1.0


def score_extraction(
    results: list[ExtractionResult] | ExtractionError,
    expected: ExpectedExtraction,
    *,
    splitting: ExpectedSplitting | None = None,
    strict_routes: bool = True,
    experiment_index: int | None = None,
) -> FieldScores:
    split_expectation = splitting or ExpectedSplitting()
    index = (
        experiment_index
        if experiment_index is not None
        else split_expectation.primary_index
    )

    if isinstance(results, ExtractionError):
        return FieldScores(0.0, 0.0, 0.0, 0.0, 0.0, 0.0)

    if index >= len(results):
        return FieldScores(0.0, 0.0, 0.0, 0.0, 0.0, 0.0)

    result = results[index]
    return FieldScores(
        endpoint_category=score_endpoint_category(result, expected),
        route=score_route(result, expected, strict_routes=strict_routes),
        species=score_species(result, expected),
        animal_counts=score_animal_counts(result, expected),
        regulatory=score_regulatory(result, expected),
        splitting_experiments=score_splitting_experiments(results, split_expectation),
    )


def format_performance_report(report: PerformanceReport) -> str:
    lines = [
        "",
        "=" * 72,
        f"Model performance score: {report.model}",
        f"Cases: {len(report.case_scores)}",
        f"Overall weighted score: {report.overall_score * 100:.1f}%",
        "",
        "Field breakdown (average score x weight = contribution):",
    ]

    averages = report.field_averages()
    contributions = report.weighted_field_contributions()
    for name in FIELD_WEIGHTS:
        weight_pct = FIELD_WEIGHTS[name] * 100
        avg_pct = averages[name] * 100
        contrib_pct = contributions[name] * 100
        passed = sum(1 for case in report.case_scores if case.field_scores.as_dict()[name] == 1.0)
        lines.append(
            f"  {name:24} {weight_pct:5.1f}%  "
            f"avg {avg_pct:5.1f}%  contrib {contrib_pct:5.1f}%  ({passed}/{len(report.case_scores)})"
        )

    lines.append("")
    lines.append("Per-case weighted scores:")
    for case in report.case_scores:
        status = "ERROR" if case.extraction_error else f"{case.weighted_total * 100:.1f}%"
        extra = f"  [{case.extraction_error}]" if case.extraction_error else ""
        count_note = (
            f"  ({case.experiment_count} experiment(s))"
            if case.experiment_count is not None
            else ""
        )
        lines.append(f"  {case.case_name:36} {status}{count_note}{extra}")

    lines.append("=" * 72)
    return "\n".join(lines)
