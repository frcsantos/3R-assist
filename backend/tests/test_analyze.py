from fastapi.testclient import TestClient

from app.adapters.llm import StubLLMAdapter
from app.api.deps import get_extraction_service, get_retrieval_service
from app.main import create_app
from app.services.extraction import ExtractionService

SAMPLE_TEXT = (
    "Acute toxicity LD50 study with 60 male Wistar rats; single dose via "
    "oral gavage and intraperitoneal injection; OECD regulatory testing."
)


class _EmptyRetrieval:
    async def search(self, _params):
        return [], None


def test_analyze_returns_parameters():
    app = create_app()
    app.dependency_overrides[get_extraction_service] = lambda: ExtractionService(
        llm=StubLLMAdapter()
    )
    app.dependency_overrides[get_retrieval_service] = lambda: _EmptyRetrieval()
    client = TestClient(app)

    response = client.post("/analyze", json={"protocol_text": SAMPLE_TEXT, "lang": "en"})

    assert response.status_code == 200
    data = response.json()
    assert len(data["experiments"]) >= 1
    assert data["params"]["endpoint_category"] == "acute_toxicity"
    assert data["params"]["route"] == ["oral", "intraperitoneal"]
    assert data["params"]["species"] == "rat"
    assert data["params"]["n_animals"] == 60
    assert data["params"]["regulatory"] is True
    assert data["experiments"][0]["raw"]["study_type"]
    assert data["lang"] == "en"


def test_analyze_rejects_short_text():
    app = create_app()
    app.dependency_overrides[get_retrieval_service] = lambda: _EmptyRetrieval()
    client = TestClient(app)

    response = client.post("/analyze", json={"protocol_text": "too short"})

    assert response.status_code == 422


def test_analyze_extraction_failed_envelope():
    app = create_app()
    app.dependency_overrides[get_extraction_service] = lambda: ExtractionService(
        llm=StubLLMAdapter()
    )
    app.dependency_overrides[get_retrieval_service] = lambda: _EmptyRetrieval()
    client = TestClient(app)

    response = client.post(
        "/analyze",
        json={
            "protocol_text": "x" * 25,
            "lang": "en",
        },
    )

    assert response.status_code == 422
    body = response.json()
    assert body["error"]["code"] == "EXTRACTION_FAILED"
