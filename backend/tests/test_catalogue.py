from fastapi.testclient import TestClient

from app.api.deps import get_document_repository, get_method_repository
from app.main import create_app
from app.models.document import Document
from app.models.i18n import localized_str
from app.models.method import Method, MethodRegulatoryContext


class StubMethodRepository:
    async def list_with_contexts(self, *, active_only: bool = False):
        _ = active_only
        method = Method(
            id=1,
            slug="oecd-tg439",
            name=localized_str("Reconstructed epidermis", "Epiderme reconstruída"),
            description=localized_str("Skin irritation method", "Método de irritação cutânea"),
            text_for_embedding="skin irritation",
            endpoint_category="skin_irritation",
            study_domain="general",
            source_db="OECD_TG",
            oecd_ref="TG 439",
            validation_status="validated",
            active=True,
            embedding_json=[0.1, 0.2],
        )
        contexts = [
            MethodRegulatoryContext(
                jurisdiction="oecd",
                regulatory_body="OECD",
                regulatory_citation="OECD TG 439",
            )
        ]
        return [method], {1: contexts}


class StubDocumentRepository:
    def __init__(self):
        self.documents = [
            Document(
                id=1,
                slug="rn-18-2014",
                doc_citation=localized_str("RN 18/2014"),
                date=None,
                categories=["regulation"],
                url="https://example.org/rn18",
            ),
            Document(
                id=2,
                slug="oecd-tg439",
                doc_citation=localized_str("OECD TG 439"),
                date=None,
                categories=["method_protocol"],
                url=None,
            ),
            Document(
                id=3,
                slug="gd-129",
                doc_citation=localized_str("OECD GD 129"),
                date=None,
                categories=["guideline"],
                url=None,
            ),
        ]

    async def list_all(self, *, categories: list[str] | None = None):
        if categories:
            wanted = set(categories)
            return [
                doc
                for doc in self.documents
                if wanted.intersection(doc.categories)
            ]
        return list(self.documents)


def _client() -> TestClient:
    app = create_app()
    app.dependency_overrides[get_method_repository] = StubMethodRepository
    app.dependency_overrides[get_document_repository] = StubDocumentRepository
    return TestClient(app)


def test_list_methods_catalogue(monkeypatch):
    monkeypatch.setenv("DATABASE_URL", "postgresql://test")
    from app.config import get_settings

    get_settings.cache_clear()
    client = _client()
    response = client.get("/methods?lang=pt")
    assert response.status_code == 200
    body = response.json()
    assert len(body["methods"]) == 1
    method = body["methods"][0]["method"]
    assert method["slug"] == "oecd-tg439"
    assert method["name"]["pt-br"] == "Epiderme reconstruída"
    assert "embedding_json" not in method
    assert "text_for_embedding" not in method
    assert body["methods"][0]["regulatory_contexts"][0]["jurisdiction"] == {
        "en-us": "OECD",
        "pt-br": "OCDE",
    }
    get_settings.cache_clear()


def test_list_documents_filtered(monkeypatch):
    monkeypatch.setenv("DATABASE_URL", "postgresql://test")
    from app.config import get_settings

    get_settings.cache_clear()
    client = _client()
    response = client.get(
        "/documents",
        params=[("category", "regulation"), ("category", "guideline")],
    )
    assert response.status_code == 200
    refs = [
        doc["doc_citation"]["en-us"]
        for doc in response.json()["documents"]
    ]
    assert set(refs) == {"OECD GD 129", "RN 18/2014"}
    assert "OECD TG 439" not in refs
    get_settings.cache_clear()
