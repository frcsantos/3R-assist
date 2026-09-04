"""Unit tests for weighted extraction reliability scoring."""

import pytest

from app.models.protocol import AnimalCounts, ExtractionResult, RawExtraction
from tests.extraction_score import (
    FIELD_WEIGHTS,
    CaseScore,
    FieldScores,
    animal_counts_match,
    build_performance_report,
    format_performance_report,
    record_case_score,
    reset_session_scores,
    score_extraction,
)
from tests.fixtures.ground_truth import ExpectedAnimalCounts, ExpectedExtraction, ExpectedSplitting


def _result(**kwargs) -> ExtractionResult:
    raw_fields = set(RawExtraction.model_fields)
    raw = RawExtraction(**{k: v for k, v in kwargs.items() if k in raw_fields})
    return ExtractionResult(
        raw=raw,
        endpoint_category=kwargs.get("endpoint_category"),
    )


def test_field_weights_sum_to_one():
    assert sum(FIELD_WEIGHTS.values()) == 1.0


def test_perfect_extraction_scores_one():
    expected = ExpectedExtraction(
        study_type_keywords=("acute toxicity",),
        endpoint_category="acute_toxicity",
        route=["oral"],
        application={"basic-research"},
        procedure_keywords=(),
        species="rat",
        animal_counts=ExpectedAnimalCounts(total=60),
        regulatory=True,
    )
    results = [
        _result(
            study_type="acute toxicity LD50 study",
            route=["oral"],
            application="basic-research",
            species="rat",
            animal_counts=AnimalCounts(total=60),
            regulatory=True,
            endpoint_category="acute_toxicity",
        )
    ]
    scores = score_extraction(results, expected)
    assert scores.weighted_total == 1.0


def test_partial_field_scores_weight_correctly():
    expected = ExpectedExtraction(
        study_type_keywords=("acute toxicity",),
        endpoint_category="acute_toxicity",
        route=["oral", "intraperitoneal"],
        application={"basic-research"},
        procedure_keywords=(),
        species="rat",
        animal_counts=ExpectedAnimalCounts(total=60),
        regulatory=True,
    )
    results = [
        _result(
            study_type="acute toxicity LD50 study",
            route=["oral"],
            application="basic-research",
            species="mouse",
            animal_counts=AnimalCounts(total=60),
            regulatory=False,
            endpoint_category="acute_toxicity",
        )
    ]
    scores = score_extraction(results, expected)
    assert scores.endpoint_category == 1.0
    assert scores.route == 0.0
    assert scores.species == 0.0
    assert scores.animal_counts == 1.0
    assert scores.regulatory == 0.0
    assert scores.splitting_experiments == 1.0
    assert scores.weighted_total == pytest.approx(0.60)


def test_regulatory_not_scored_when_expected_null():
    expected = ExpectedExtraction(
        study_type_keywords=("prenatal",),
        endpoint_category=None,
        route=["oral"],
        application={"basic-research"},
        procedure_keywords=(),
        species="rat",
        animal_counts=None,
        regulatory=None,
    )
    results = [
        _result(
            study_type="prenatal developmental toxicity study",
            route=["oral"],
            application="basic-research",
            species="rat",
            regulatory=True,
            endpoint_category=None,
        )
    ]
    scores = score_extraction(results, expected)
    assert scores.regulatory == 1.0


def test_splitting_requires_minimum_experiment_count():
    expected = ExpectedExtraction(
        study_type_keywords=("acute toxicity",),
        endpoint_category="acute_toxicity",
        route=["oral"],
        application={"basic-research"},
        procedure_keywords=(),
        species="rat",
        animal_counts=ExpectedAnimalCounts(total=60),
        regulatory=True,
    )
    results = [
        _result(
            study_type="acute toxicity LD50 study",
            route=["oral"],
            application="basic-research",
            species="rat",
            animal_counts=AnimalCounts(total=60),
            regulatory=True,
            endpoint_category="acute_toxicity",
        )
    ]
    scores = score_extraction(
        results,
        expected,
        splitting=ExpectedSplitting(min_count=2, max_count=None),
    )
    assert scores.splitting_experiments == 0.0
    assert scores.endpoint_category == 1.0


def test_empty_animal_counts_match_expected_none():
    assert animal_counts_match(AnimalCounts(), None)
    assert animal_counts_match(
        AnimalCounts(female=None, male=None, total=None, per_group=None),
        None,
    )


def test_animal_counts_total_derived_from_female_and_male():
    expected = ExpectedExtraction(
        study_type_keywords=("prenatal",),
        endpoint_category=None,
        route=["oral"],
        application={"basic-research"},
        procedure_keywords=(),
        species="rat",
        animal_counts=ExpectedAnimalCounts(female=100, male=60, total=160),
        regulatory=True,
    )
    results = [
        _result(
            study_type="prenatal developmental toxicity study",
            route=["oral"],
            application="basic-research",
            species="rat",
            animal_counts=AnimalCounts(female=100, male=60),
            regulatory=True,
            endpoint_category=None,
        )
    ]
    scores = score_extraction(results, expected)
    assert scores.animal_counts == 1.0


def test_performance_report_aggregation_and_formatting():
    reset_session_scores()
    perfect = FieldScores(1.0, 1.0, 1.0, 1.0, 1.0, 1.0)
    partial = FieldScores(1.0, 0.0, 1.0, 0.0, 1.0, 1.0)
    record_case_score(CaseScore("perfect case", "test/model", perfect, experiment_count=1))
    record_case_score(CaseScore("partial case", "test/model", partial, experiment_count=1))

    report = build_performance_report("test/model")
    assert report.overall_score == pytest.approx(0.85)
    rendered = format_performance_report(report)
    assert "Model performance score: test/model" in rendered
    assert "Overall weighted score: 85.0%" in rendered
    assert "animal_counts" in rendered
