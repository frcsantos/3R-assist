"""Reliability tests for LLM parameter extraction against curated ground truth.

Run live tests (real API calls):
    pytest tests/test_extraction_reliability.py -v -s -m live

After a live run, a weighted model performance score is printed at the end.
"""
from __future__ import annotations

import pytest

from app.adapters.llm import ExtractionError, format_extraction_error
from app.models.protocol import ExtractionResult
from app.services.extraction import enrich_raw_experiments
from tests.extraction_score import (
    CaseScore,
    animal_counts_match,
    record_case_score,
    score_extraction,
)
from tests.fixtures.benzophenone_reproductive_protocol import (
    BENZOPHENONE_REPRODUCTIVE_PROTOCOL,
    EXPECTED_BENZOPHENONE_REPRODUCTIVE,
)
from tests.fixtures.carbon_black_protocol import (
    CARBON_BLACK_PROTOCOL,
    EXPECTED_CARBON_BLACK_INHALATION,
)
from tests.fixtures.eveit_protocol import EVEIT_PROTOCOL, EXPECTED_EVEIT
from tests.fixtures.genotoxicity_battery_protocol import (
    EXPECTED_GENOTOXICITY_BATTERY,
    GENOTOXICITY_BATTERY_PROTOCOL,
)
from tests.fixtures.prenatal_allulose_protocol import (
    EXPECTED_PRENATAL_ALLULOSE,
    PRENATAL_ALLULOSE_PROTOCOL,
)
from tests.fixtures.uv_photocarcinogenesis_protocol import (
    EXPECTED_UV_PHOTOCARCINOGENESIS,
    UV_PHOTOCARCINOGENESIS_PROTOCOL,
)
from tests.fixtures.ground_truth import (
    ExpectedEvidence,
    ExpectedExtraction,
    ExpectedSplitting,
)
from tests.fixtures.parthenium_protocol import (
    EXPECTED_ACUTE,
    EXPECTED_SUBACUTE,
    PARTHENIUM_ACUTE_SECTION,
    PARTHENIUM_FULL_PROTOCOL,
    PARTHENIUM_SUBACUTE_SECTION,
)


def _evidence_matches(got: str | None, expected_fragment: str | tuple[str, ...]) -> bool:
    if got is None:
        return False
    fragments = (
        (expected_fragment,)
        if isinstance(expected_fragment, str)
        else expected_fragment
    )
    got_lower = got.lower()
    return any(fragment.lower() in got_lower for fragment in fragments)


def _assert_evidence_fields(
    raw,
    expected: ExpectedEvidence,
    mismatches: list[str],
) -> None:
    field_map = {
        "route": raw.route_evidence,
        "application": raw.application_evidence,
        "procedure_text": raw.procedure_text_evidence,
        "species": raw.species_evidence,
        "animal_counts": raw.animal_counts_evidence,
        "regulatory": raw.regulatory_evidence,
    }
    for field_name, fragment in expected.__dict__.items():
        if fragment is None:
            continue
        got = field_map[field_name]
        if not _evidence_matches(got, fragment):
            mismatches.append(
                f"{field_name}_evidence: got {got!r}, expected substring {fragment!r}"
            )


def _assert_extraction_matches(
    result: ExtractionResult,
    expected: ExpectedExtraction,
    *,
    label: str,
    strict_routes: bool = True,
) -> None:
    raw = result.raw
    mismatches: list[str] = []

    study_type = (raw.study_type or "").lower()
    if expected.study_type_keywords and not any(
        keyword.lower() in study_type for keyword in expected.study_type_keywords
    ):
        mismatches.append(
            f"study_type: got {raw.study_type!r}, expected one of "
            f"{expected.study_type_keywords!r}"
        )

    if result.endpoint_category != expected.endpoint_category:
        mismatches.append(
            f"endpoint_category: got {result.endpoint_category!r}, "
            f"expected {expected.endpoint_category!r}"
        )

    if expected.route is not None:
        got_routes = set(raw.route or [])
        want_routes = set(expected.route)
        if not want_routes.issubset(got_routes):
            mismatches.append(
                f"route: got {sorted(got_routes)!r}, missing "
                f"{sorted(want_routes - got_routes)!r}"
            )
        elif strict_routes and got_routes != want_routes:
            mismatches.append(
                f"route: got {sorted(got_routes)!r}, expected exactly "
                f"{sorted(want_routes)!r}"
            )
    elif raw.route:
        mismatches.append(
            f"route: got {raw.route!r}, expected null"
        )

    if raw.application not in expected.application:
        mismatches.append(
            f"application: got {raw.application!r}, "
            f"expected one of {sorted(expected.application)!r}"
        )

    if raw.species != expected.species:
        mismatches.append(
            f"species: got {raw.species!r}, expected {expected.species!r}"
        )

    if not animal_counts_match(raw.animal_counts, expected.animal_counts):
        mismatches.append(
            f"animal_counts: got {raw.animal_counts!r}, "
            f"expected {expected.animal_counts!r}"
        )

    if expected.regulatory is not None and raw.regulatory != expected.regulatory:
        mismatches.append(
            f"regulatory: got {raw.regulatory!r}, expected {expected.regulatory!r}"
        )

    procedure = (raw.procedure_text or "").lower()
    if expected.procedure_keywords and not any(
        keyword in procedure for keyword in expected.procedure_keywords
    ):
        mismatches.append(
            f"procedure_text: {raw.procedure_text!r} missing keywords "
            f"{expected.procedure_keywords!r}"
        )

    if expected.evidence is not None:
        _assert_evidence_fields(raw, expected.evidence, mismatches)

    if mismatches:
        detail = "\n".join(f"  - {item}" for item in mismatches)
        pytest.fail(f"{label} extraction mismatches:\n{detail}")


def _record_reliability_score(
    *,
    case_name: str,
    model: str,
    results: list[ExtractionResult] | ExtractionError,
    expected: ExpectedExtraction,
    splitting: ExpectedSplitting | None = None,
    strict_routes: bool = True,
    experiment_index: int | None = None,
    extraction_error: str | None = None,
) -> None:
    field_scores = score_extraction(
        results,
        expected,
        splitting=splitting,
        strict_routes=strict_routes,
        experiment_index=experiment_index,
    )
    experiment_count = None if isinstance(results, ExtractionError) else len(results)
    record_case_score(
        CaseScore(
            case_name=case_name,
            model=model,
            field_scores=field_scores,
            extraction_error=extraction_error,
            experiment_count=experiment_count,
        )
    )


def _extract_score_and_assert(
    adapter,
    model: str,
    *,
    case_name: str,
    protocol: str,
    expected: ExpectedExtraction,
    splitting: ExpectedSplitting | None = None,
    strict_routes: bool = True,
    experiment_index: int | None = None,
) -> ExtractionResult:
    label = f"[{model}] {case_name}"
    split_expectation = splitting or ExpectedSplitting()
    index = (
        experiment_index
        if experiment_index is not None
        else split_expectation.primary_index
    )
    raw_results = adapter.extract_raw_experiments(protocol)
    if isinstance(raw_results, ExtractionError):
        _record_reliability_score(
            case_name=case_name,
            model=model,
            results=raw_results,
            expected=expected,
            splitting=split_expectation,
            strict_routes=strict_routes,
            experiment_index=index,
            extraction_error=raw_results.message,
        )
        pytest.fail(f"{label} failed:\n{format_extraction_error(raw_results)}")

    results = enrich_raw_experiments(raw_results)
    _record_reliability_score(
        case_name=case_name,
        model=model,
        results=results,
        expected=expected,
        splitting=split_expectation,
        strict_routes=strict_routes,
        experiment_index=index,
    )

    if index >= len(results):
        pytest.fail(
            f"{label} returned {len(results)} experiment(s); expected index {index}"
        )

    result = results[index]
    _assert_extraction_matches(
        result,
        expected,
        label=label,
        strict_routes=strict_routes,
    )
    return result


def test_evidence_matches_accepts_minimal_substring_or_any_tuple_option():
    assert _evidence_matches("Wistar rats", "wistar")
    assert _evidence_matches(
        "administered p.o. by gastric tube",
        ("p.o.", "i.p."),
    )
    assert _evidence_matches(
        "Groups of 5 F344 male rats were treated by gavage",
        ("comet", "gavage", "safrole"),
    )
    assert not _evidence_matches("SD rats", ("female", "100"))


@pytest.mark.live
def test_parthenium_full_protocol_prioritizes_acute_toxicity(live_llm_adapter):
    """From a multi-experiment paper, extraction should surface the LD50 study."""
    adapter, model = live_llm_adapter
    _extract_score_and_assert(
        adapter,
        model,
        case_name="parthenium full",
        protocol=PARTHENIUM_FULL_PROTOCOL,
        expected=EXPECTED_ACUTE,
        splitting=ExpectedSplitting(min_count=2, max_count=None, primary_index=0),
    )


@pytest.mark.live
def test_parthenium_acute_section_extraction(live_llm_adapter):
    adapter, model = live_llm_adapter
    _extract_score_and_assert(
        adapter,
        model,
        case_name="parthenium acute",
        protocol=PARTHENIUM_ACUTE_SECTION,
        expected=EXPECTED_ACUTE,
    )


@pytest.mark.live
def test_parthenium_subacute_section_no_endpoint_match(live_llm_adapter):
    """28-day repeated-dose study has no endpoint_category in current vocabulary."""
    adapter, model = live_llm_adapter
    _extract_score_and_assert(
        adapter,
        model,
        case_name="parthenium subacute",
        protocol=PARTHENIUM_SUBACUTE_SECTION,
        expected=EXPECTED_SUBACUTE,
    )


@pytest.mark.live
def test_carbon_black_inhalation_no_endpoint_match(live_llm_adapter):
    """90-day repeated-dose inhalation has no endpoint_category in current vocabulary."""
    adapter, model = live_llm_adapter
    _extract_score_and_assert(
        adapter,
        model,
        case_name="carbon black inhalation",
        protocol=CARBON_BLACK_PROTOCOL,
        expected=EXPECTED_CARBON_BLACK_INHALATION,
    )


@pytest.mark.live
def test_eveit_ocular_irritation_extraction(live_llm_adapter):
    """Ex vivo bovine cornea model should map to ocular_irritation with species other."""
    adapter, model = live_llm_adapter
    _extract_score_and_assert(
        adapter,
        model,
        case_name="EVEIT",
        protocol=EVEIT_PROTOCOL,
        expected=EXPECTED_EVEIT,
    )


@pytest.mark.live
def test_genotoxicity_battery_extraction(live_llm_adapter):
    """Multi-assay comet + micronucleus battery should map to genotoxicity via oral gavage."""
    adapter, model = live_llm_adapter
    _extract_score_and_assert(
        adapter,
        model,
        case_name="genotoxicity battery",
        protocol=GENOTOXICITY_BATTERY_PROTOCOL,
        expected=EXPECTED_GENOTOXICITY_BATTERY,
        splitting=ExpectedSplitting(min_count=1, max_count=1),
    )


@pytest.mark.live
def test_prenatal_allulose_no_endpoint_match(live_llm_adapter):
    """OECD TG 414 prenatal study has no endpoint_category in current vocabulary."""
    adapter, model = live_llm_adapter
    _extract_score_and_assert(
        adapter,
        model,
        case_name="prenatal allulose",
        protocol=PRENATAL_ALLULOSE_PROTOCOL,
        expected=EXPECTED_PRENATAL_ALLULOSE,
    )


@pytest.mark.live
def test_benzophenone_reproductive_no_endpoint_match(live_llm_adapter):
    """Two-generation reproductive study (TG 416-class) has no endpoint_category in vocabulary."""
    adapter, model = live_llm_adapter
    _extract_score_and_assert(
        adapter,
        model,
        case_name="benzophenone reproductive",
        protocol=BENZOPHENONE_REPRODUCTIVE_PROTOCOL,
        expected=EXPECTED_BENZOPHENONE_REPRODUCTIVE,
    )


@pytest.mark.live
def test_uv_photocarcinogenesis_no_endpoint_or_route(live_llm_adapter):
    """Chronic UV tumor bioassay has no endpoint_category and no chemical route."""
    adapter, model = live_llm_adapter
    _extract_score_and_assert(
        adapter,
        model,
        case_name="UV photocarcinogenesis",
        protocol=UV_PHOTOCARCINOGENESIS_PROTOCOL,
        expected=EXPECTED_UV_PHOTOCARCINOGENESIS,
    )
