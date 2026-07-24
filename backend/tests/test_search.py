from fastapi.testclient import TestClient

from app.adapters.embedder import StubEmbedderAdapter
from app.api.deps import get_retrieval_service
from app.main import create_app
from app.models.method import Method, MethodRegulatoryContext
from app.repositories.methods import MethodRepository
from app.services.retrieval import RetrievalService


def _context(
    jurisdiction: str = "oecd",
    *,
    study_domain: str = "general",
    validation_status: str = "validated",
) -> MethodRegulatoryContext:
    return MethodRegulatoryContext(
        study_domain=study_domain,
        jurisdiction=jurisdiction,
        validation_status=validation_status,
        regulatory_body="OECD",
        regulation_date=None,
        regulatory_url="https://example.org/tg420",
    )


def _rationales_from_classes(category_3r: list[str] | None) -> dict[str, str]:
    classes = category_3r or ["replacement"]
    return {f"{r}_rationale": f"Test rationale for {r}" for r in classes}


def _method(
    slug: str,
    endpoint: str,
    routes: list[str] | None,
    *,
    method_id: int = 1,
    category_3r: list[str] | None = None,
    contexts: list[MethodRegulatoryContext] | None = None,
) -> tuple[Method, list[MethodRegulatoryContext]]:
    method = Method(
        id=method_id,
        slug=slug,
        name_en=f"{slug} EN",
        name_pt=f"{slug} PT",
        description_en="desc",
        description_pt="desc",
        text_for_embedding="acute oral LD50",
        endpoint_category=endpoint,
        study_domain="general",
        source_db="NICEATM",
        routes_applicable=routes,
        active=True,
        **_rationales_from_classes(category_3r),
    )
    return method, contexts or [_context("oecd"), _context("brazil")]


class FakeMethodRepository(MethodRepository):
    def __init__(self, entries: list[tuple[Method, list[MethodRegulatoryContext]]]) -> None:
        self._entries = entries

    async def list_active(self) -> list[Method]:
        methods, _ = await self.list_active_with_contexts()
        return methods

    async def list_active_with_contexts(
        self,
    ) -> tuple[list[Method], dict[int, list[MethodRegulatoryContext]]]:
        methods = [entry[0] for entry in self._entries]
        contexts = {entry[0].id: entry[1] for entry in self._entries}
        return methods, contexts


def _search_client(entries: list[tuple[Method, list[MethodRegulatoryContext]]]) -> TestClient:
    service = RetrievalService(
        FakeMethodRepository(entries),
        StubEmbedderAdapter(),
        semantic_ranking=False,
    )
    app = create_app()
    app.dependency_overrides[get_retrieval_service] = lambda: service
    return TestClient(app)


def test_search_returns_ranked_recommendations():
    entries = [
        _method("oral-a", "acute_toxicity", ["oral"], method_id=1),
        _method("oral-b", "acute_toxicity", ["oral"], method_id=2),
        _method("oral-c", "acute_toxicity", ["oral"], method_id=3),
    ]
    client = _search_client(entries)

    response = client.post(
        "/search",
        json={
            "params": {
                "endpoint_category": "acute_toxicity",
                "route": ["oral"],
                "study_domain": "general",
                "procedure_text": "LD50 single dose",
            }
        },
    )

    assert response.status_code == 200
    data = response.json()
    assert len(data["results"]) == 3
    assert data["results"][0]["rank"] == 1
    assert data["results"][0]["method"]["slug"] == "oral-a"
    assert data["results"][0]["score"] > 0
    assert data["results"][0]["regulatory_contexts"]


def test_search_applies_three_r_filter():
    entries = [
        _method("replace", "acute_toxicity", ["oral"], method_id=1, category_3r=["replacement"]),
        _method("reduce", "acute_toxicity", ["oral"], method_id=2, category_3r=["reduction"]),
        _method(
            "both",
            "acute_toxicity",
            ["oral"],
            method_id=3,
            category_3r=["reduction", "refinement"],
        ),
    ]
    client = _search_client(entries)

    response = client.post(
        "/search",
        json={
            "params": {
                "endpoint_category": "acute_toxicity",
                "route": ["oral"],
                "study_domain": "general",
            },
            "filters": {"three_r_class": "replacement"},
        },
    )

    assert response.status_code == 200
    results = response.json()["results"]
    assert len(results) == 1
    assert results[0]["method"]["category_3r"] == ["replacement"]


def test_search_applies_jurisdiction_filter():
    entries = [
        _method(
            "brazil-only",
            "acute_toxicity",
            ["oral"],
            method_id=1,
            contexts=[_context("brazil")],
        ),
        _method(
            "oecd-only",
            "acute_toxicity",
            ["oral"],
            method_id=2,
            contexts=[_context("oecd")],
        ),
    ]
    client = _search_client(entries)

    response = client.post(
        "/search",
        json={
            "params": {
                "endpoint_category": "acute_toxicity",
                "study_domain": "general",
            },
            "filters": {"jurisdiction": "brazil"},
        },
    )

    assert response.status_code == 200
    results = response.json()["results"]
    assert len(results) == 1
    assert results[0]["method"]["slug"] == "brazil-only"


def test_search_without_database_returns_503(monkeypatch):
    monkeypatch.setenv("DATABASE_URL", "")
    from app.config import get_settings

    get_settings.cache_clear()

    app = create_app()
    client = TestClient(app)
    response = client.post(
        "/search",
        json={
            "params": {
                "endpoint_category": "acute_toxicity",
                "study_domain": "general",
            }
        },
    )

    assert response.status_code == 503
    assert response.json()["error"]["code"] == "DATABASE_UNAVAILABLE"

    get_settings.cache_clear()
