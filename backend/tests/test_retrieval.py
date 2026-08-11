import asyncio

from app.adapters.embedder import StubEmbedderAdapter
from app.models.i18n import localized_str
from app.models.method import Method
from app.models.protocol import ProtocolParameters
from app.repositories.methods import MethodRepository
from app.services.retrieval import (
    RetrievalService,
    build_query_text,
    cosine_similarity,
    filter_only_score,
)


def _method(
    slug: str,
    endpoint: str,
    routes: list[str] | None,
    *,
    method_id: int = 1,
    embedding: list[float] | None = None,
    text_for_embedding: str = "text",
) -> Method:
    return Method(
        id=method_id,
        slug=slug,
        name=localized_str(slug),
        description=localized_str("desc"),
        text_for_embedding=text_for_embedding,
        reduction_rationale=localized_str("Test reduction rationale"),
        endpoint_category=endpoint,
        study_domain="general",
        source_db="NICEATM",
        routes_applicable=routes,
        embedding_json=embedding,
        validation_status="validated",
        active=True,
    )


class FakeMethodRepository(MethodRepository):
    def __init__(self, methods: list[Method]) -> None:
        self._methods = methods

    async def list_active(self) -> list[Method]:
        return self._methods

    async def list_active_with_contexts(self):
        return self._methods, {}


def test_build_query_text_includes_matching_fields():
    params = ProtocolParameters(
        endpoint_category="acute_toxicity",
        route=["oral"],
        study_domain="general",
        procedure_text="LD50 single dose",
    )
    text = build_query_text(params)
    assert "acute_toxicity" in text
    assert "LD50 single dose" in text
    assert "oral" in text


def test_cosine_similarity_for_identical_vectors():
    vector = [0.5, 0.5, 0.5, 0.5]
    assert cosine_similarity(vector, vector) == 1.0


def test_filter_only_retrieval_without_embeddings():
    methods = [
        _method("oral-a", "acute_toxicity", ["oral"], method_id=1),
        _method("oral-b", "acute_toxicity", ["oral"], method_id=2),
        _method("oral-c", "acute_toxicity", ["oral"], method_id=3),
        _method("dermal-a", "skin_irritation", ["dermal"], method_id=4),
    ]
    service = RetrievalService(
        FakeMethodRepository(methods),
        StubEmbedderAdapter(),
        semantic_ranking=False,
    )
    params = ProtocolParameters(
        endpoint_category="acute_toxicity",
        route=["oral"],
        study_domain="general",
        procedure_text="LD50",
    )

    recommendations, relaxation = asyncio.run(service.search(params))

    assert relaxation is None
    assert len(recommendations) == 3
    assert all(item.method.endpoint_category == "acute_toxicity" for item in recommendations)


def test_filter_only_score_uses_procedure_overlap():
    method = _method(
        "a",
        "acute_toxicity",
        ["oral"],
        text_for_embedding="acute oral LD50 fixed dose OECD",
    )
    params = ProtocolParameters(
        endpoint_category="acute_toxicity",
        route=["oral"],
        study_domain="general",
        procedure_text="LD50 fixed dose oral",
    )
    assert filter_only_score(method, params) > filter_only_score(
        _method("b", "acute_toxicity", ["oral"], text_for_embedding="unrelated words only"),
        params,
    )


def test_retrieval_filters_endpoint_and_route():
    embedder = StubEmbedderAdapter()
    oral_vector = embedder.embed("acute_toxicity oral general")
    dermal_vector = embedder.embed("skin_irritation dermal general")

    methods = [
        _method("oral-a", "acute_toxicity", ["oral"], method_id=1, embedding=oral_vector),
        _method("oral-b", "acute_toxicity", ["oral"], method_id=2, embedding=oral_vector),
        _method("oral-c", "acute_toxicity", ["oral"], method_id=3, embedding=oral_vector),
        _method("dermal-a", "skin_irritation", ["dermal"], method_id=4, embedding=dermal_vector),
    ]
    service = RetrievalService(
        FakeMethodRepository(methods),
        embedder,
        semantic_ranking=True,
    )
    params = ProtocolParameters(
        endpoint_category="acute_toxicity",
        route=["oral"],
        study_domain="general",
        procedure_text="LD50",
    )

    recommendations, relaxation = asyncio.run(service.search(params))

    assert relaxation is None
    assert len(recommendations) == 3
    assert all(item.method.endpoint_category == "acute_toxicity" for item in recommendations)


def test_retrieval_relaxes_route_filter_for_minimum_results():
    embedder = StubEmbedderAdapter()
    vector = embedder.embed("acute_toxicity oral general")

    methods = [
        _method("a", "acute_toxicity", ["oral"], method_id=1, embedding=vector),
        _method("b", "acute_toxicity", ["oral"], method_id=2, embedding=vector),
        _method("c", "acute_toxicity", ["oral"], method_id=3, embedding=vector),
    ]
    service = RetrievalService(
        FakeMethodRepository(methods),
        embedder,
        semantic_ranking=True,
    )
    params = ProtocolParameters(
        endpoint_category="acute_toxicity",
        route=["intraperitoneal"],
        study_domain="general",
    )

    recommendations, relaxation = asyncio.run(service.search(params))

    assert relaxation == "route_filter_relaxed"
    assert len(recommendations) == 3
