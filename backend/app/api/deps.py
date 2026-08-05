from functools import lru_cache

from app.adapters.embedder import EmbedderAdapter, build_embedder
from app.adapters.llm import LLMAdapter, build_llm_adapter
from app.config import get_settings
from app.repositories.admin import AdminRepository
from app.repositories.documents import DocumentRepository
from app.repositories.methods import MethodRepository
from app.services.extraction import ExtractionService
from app.services.method_draft_extraction import MethodDraftExtractionService
from app.services.policy_document_match import PolicyDocumentMatchService
from app.services.policy_extraction import PolicyExtractionService
from app.services.policy_method_match import PolicyMethodMatchService
from app.services.retrieval import RetrievalService


@lru_cache
def get_llm_adapter() -> LLMAdapter:
    settings = get_settings()
    return build_llm_adapter(
        model=settings.resolved_llm_model,
        use_stub=settings.use_stub_llm,
        ollama_model=settings.ollama_model,
    )


@lru_cache
def get_embedder() -> EmbedderAdapter:
    return build_embedder()


@lru_cache
def get_method_repository() -> MethodRepository:
    return MethodRepository()


@lru_cache
def get_document_repository() -> DocumentRepository:
    return DocumentRepository()


def get_admin_repository() -> AdminRepository:
    return AdminRepository()


def get_extraction_service() -> ExtractionService:
    return ExtractionService(llm=get_llm_adapter())


def get_policy_extraction_service() -> PolicyExtractionService:
    return PolicyExtractionService(llm=get_llm_adapter())


def get_method_draft_extraction_service() -> MethodDraftExtractionService:
    return MethodDraftExtractionService(llm=get_llm_adapter())


def get_policy_method_match_service() -> PolicyMethodMatchService:
    return PolicyMethodMatchService(repository=get_method_repository())


def get_policy_document_match_service() -> PolicyDocumentMatchService:
    return PolicyDocumentMatchService(repository=get_document_repository())


def get_retrieval_service() -> RetrievalService:
    settings = get_settings()
    return RetrievalService(
        repository=get_method_repository(),
        embedder=get_embedder(),
        semantic_ranking=settings.semantic_ranking,
    )
