"""Composite scoring: endpoint hierarchy, animal use, avoided procedures, current method."""

import asyncio

import pytest

from app.adapters.embedder import StubEmbedderAdapter
from app.models.i18n import localized_str
from app.models.method import Method
from app.models.protocol import ProtocolParameters, RawExtraction
from app.repositories.methods import MethodRepository
from app.services import vocabulary
from app.services.extraction import enrich_raw_extraction
from app.services.retrieval import RetrievalService, score_method

TREE = [
    vocabulary.EndpointRow(1, "human-health-effects", None, "2", {"en-us": "Human health effects"}),
    vocabulary.EndpointRow(2, "local-effects", "human-health-effects", "2.1", {"en-us": "Local effects"}),
    vocabulary.EndpointRow(3, "eye-effects", "local-effects", "2.1.2", {"en-us": "Eye effects"}),
    vocabulary.EndpointRow(4, "eye-irritation", "eye-effects", "2.1.2.1", {"en-us": "Eye irritation"}),
    vocabulary.EndpointRow(5, "serious-eye-damage", "eye-effects", "2.1.2.2", {"en-us": "Serious eye damage"}),
    vocabulary.EndpointRow(6, "skin-effects", "local-effects", "2.1.1", {"en-us": "Skin effects"}),
    vocabulary.EndpointRow(7, "skin-irritation", "skin-effects", "2.1.1.1", {"en-us": "Skin irritation"}),
    vocabulary.EndpointRow(8, "endocrine-activity", None, "3.1", {"en-us": "Endocrine activity"}),
    vocabulary.EndpointRow(9, "estrogenic-activity", "endocrine-activity", "3.1.1", {"en-us": "Estrogenic activity"}),
]


@pytest.fixture(autouse=True)
def endpoint_tree():
    vocabulary.set_endpoint_rows(TREE)
    yield
    vocabulary.clear_applications()


def _method(
    slug="m",
    endpoints=("eye-irritation",),
    *,
    animal_use=None,
    test_system=None,
    avoided=None,
    oecd_ref=None,
    rationale="replacement",
    routes=None,
    method_id=1,
):
    return Method(
        id=method_id,
        slug=slug,
        name=localized_str(slug),
        description=localized_str("desc"),
        text_for_embedding="text",
        endpoints=[1],
        endpoint_codes=list(endpoints),
        application_codes=["regulatory-use"],
        source_db="OECD_TG",
        oecd_ref=oecd_ref,
        animal_use=animal_use,
        test_system=test_system,
        animal_procedures_avoided=avoided or [],
        route_codes=routes or [],
        routes_applicable=None if routes is None else [1] * len(routes),
        validation_status="validated",
        active=True,
        **{f"{rationale}_rationale": "x"},
    )


def _params(**kwargs):
    return ProtocolParameters(application="regulatory-use", **kwargs)


class _Repo(MethodRepository):
    def __init__(self, methods):
        self._methods = methods

    async def list_active_with_contexts(self):
        return self._methods, {}


# --- endpoint hierarchy ----------------------------------------------------------


def test_endpoint_relation_uses_the_tree():
    relation = vocabulary.endpoint_relation
    assert relation("eye-irritation", {"eye-irritation"}) == "exact"
    # protocol asks for the group, method covers a member
    assert relation("endocrine-activity", {"estrogenic-activity"}) == "specific"
    # protocol asks for a member, method covers the group (but not the root)
    assert relation("eye-irritation", {"eye-effects"}) == "general"
    assert relation("eye-irritation", {"human-health-effects"}) is None
    # siblings do not match
    assert relation("eye-irritation", {"serious-eye-damage"}) is None
    assert relation("skin-irritation", {"eye-irritation"}) is None


def test_endpoint_relation_without_tree_is_exact_only():
    vocabulary.clear_applications()
    assert vocabulary.endpoint_relation("endocrine-activity", {"estrogenic-activity"}) is None
    assert vocabulary.endpoint_relation("a", {"a"}) == "exact"


def test_group_endpoint_finds_narrower_methods():
    narrower = _method("estrogen", ("estrogenic-activity",), animal_use="none", method_id=1)
    unrelated = _method("eye", ("eye-irritation",), animal_use="none", method_id=2)
    service = RetrievalService(_Repo([narrower, unrelated]), StubEmbedderAdapter())

    recs, relaxation = asyncio.run(service.search(_params(endpoint_category="endocrine-activity")))

    # One method covers the group: it is returned alone, not padded with the eye method.
    assert relaxation is None
    assert [rec.method.slug for rec in recs] == ["estrogen"]
    assert "endpoint_category" in recs[0].matched_params
    assert recs[0].score_breakdown["endpoint"] == 0.8


def test_unrelated_methods_are_only_shown_when_nothing_matches_the_endpoint():
    eye = _method("eye", ("eye-irritation",), animal_use="none")
    service = RetrievalService(_Repo([eye]), StubEmbedderAdapter())

    recs, relaxation = asyncio.run(service.search(_params(endpoint_category="skin-irritation")))

    assert relaxation == "endpoint_and_route_filters_relaxed"
    assert [rec.method.slug for rec in recs] == ["eye"]
    assert "endpoint_category" not in recs[0].matched_params


# --- animal use ------------------------------------------------------------------


def test_non_animal_method_outranks_live_animal_method_for_an_in_vivo_protocol():
    params = _params(endpoint_category="eye-irritation", test_system=["in_vivo"])
    replacement = score_method(_method(animal_use="none", test_system=["in_chemico"]), params)
    reduction = score_method(
        _method(animal_use="live_animals", test_system=["in_vivo"], rationale="reduction"), params
    )
    assert replacement.score > reduction.score
    assert "animal_use" in replacement.matched_params
    assert "animal_use" not in reduction.matched_params
    assert reduction.components["animal_use"] > 0  # still worth showing as reduction/refinement


def test_animal_method_gets_no_credit_when_protocol_is_already_in_vitro():
    params = _params(endpoint_category="eye-irritation", test_system=["in_vitro"])
    result = score_method(
        _method(animal_use="live_animals", test_system=["in_vivo"], rationale="reduction"), params
    )
    assert result.components["animal_use"] == 0.0


# --- avoided procedures / current method -----------------------------------------


def test_method_that_avoids_the_protocol_guideline_is_a_strong_match():
    avoided = [{"name": {"en-us": "Traditional LD50 test"}, "species": "rat", "oecd_ref": "TG 401"}]
    method = _method(
        "tg420", animal_use="live_animals", avoided=avoided, oecd_ref="TG 420", rationale="reduction"
    )
    cited = score_method(method, _params(endpoint_category="eye-irritation", guideline_ref="OECD TG 401"))
    plain = score_method(method, _params(endpoint_category="eye-irritation"))
    assert cited.components["avoided_procedure"] == 1.0
    assert "avoided_procedure" in cited.matched_params
    assert cited.score > plain.score


def test_avoided_procedure_species_gives_partial_credit():
    avoided = [{"name": {"en-us": "Rabbit pyrogen test"}, "species": "rabbit"}]
    result = score_method(
        _method(avoided=avoided), _params(endpoint_category="eye-irritation", species="rabbit")
    )
    assert result.components["avoided_procedure"] == 0.6


def test_method_the_protocol_already_follows_is_demoted():
    method = _method(animal_use="none", oecd_ref="TG 439")
    follows = score_method(
        method, _params(endpoint_category="eye-irritation", guideline_ref="OECD TG 439")
    )
    other = score_method(method, _params(endpoint_category="eye-irritation", guideline_ref="TG 431"))
    assert follows.score == pytest.approx(other.score * 0.5, abs=0.01)


# --- re-weighting ----------------------------------------------------------------


def test_missing_protocol_information_is_not_penalised():
    sparse = score_method(_method(animal_use="none"), _params(endpoint_category="eye-irritation"))
    assert "route" not in sparse.components and "text" not in sparse.components
    assert sparse.score > 0.8


# --- extraction ------------------------------------------------------------------


def test_model_endpoint_wins_over_keyword_lookup():
    raw = RawExtraction(study_type="eye irritation study", endpoint="serious-eye-damage")
    assert enrich_raw_extraction(raw).endpoint_category == "serious-eye-damage"


def test_unknown_or_root_model_endpoint_falls_back_to_lookup():
    unknown = RawExtraction(study_type="skin irritation test", endpoint="not-in-table")
    assert unknown.endpoint is None
    assert enrich_raw_extraction(unknown).endpoint_category == "skin_irritation"
    root = RawExtraction(study_type="skin irritation test", endpoint="human-health-effects")
    assert enrich_raw_extraction(root).endpoint_category == "skin_irritation"


def test_extraction_fields_are_coerced_not_rejected():
    raw = RawExtraction(
        study_type="x",
        test_system=["In-Vivo", "nonsense"],
        guideline_ref="performed under OECD tg420 (2002)",
    )
    assert raw.test_system == ["in_vivo"]
    assert raw.guideline_ref == "TG 420"
