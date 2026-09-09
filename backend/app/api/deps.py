from functools import lru_cache

from fastapi import Depends, HTTPException, Request

from app.adapters.embedder import EmbedderAdapter, build_embedder
from app.adapters.llm import LLMAdapter, build_llm_adapter
from app.config import get_settings
from app.models.user import User
from app.repositories.admin import AdminRepository
from app.repositories.documents import DocumentRepository
from app.repositories.feedback import FeedbackRepository
from app.repositories.methods import MethodRepository
from app.repositories.users import UserRepository
from app.services.auth import AuthError, AuthService
from app.services.extraction import ExtractionService
from app.services.document_draft_extraction import DocumentDraftExtractionService
from app.services.extract_estimate import ExtractEstimateService
from app.services.method_draft_extraction import MethodDraftExtractionService
from app.services.regulation_draft_extraction import RegulationDraftExtractionService
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


def get_feedback_repository() -> FeedbackRepository:
    return FeedbackRepository()


def get_user_repository() -> UserRepository:
    return UserRepository()


def get_auth_service() -> AuthService:
    return AuthService()


async def get_current_user(
    request: Request,
    repository: UserRepository = Depends(get_user_repository),
    auth: AuthService = Depends(get_auth_service),
) -> User:
    """Resolve the signed-in user from the Authorization bearer token.

    Returns 404 while the user system is disabled, and 401 for missing or
    invalid credentials once it is enabled.
    """
    if not get_settings().user_system_enabled:
        raise HTTPException(status_code=404, detail="Not Found")
    header = request.headers.get("Authorization", "")
    token = header.removeprefix("Bearer").strip()
    if not token:
        raise HTTPException(status_code=401, detail="Not authenticated")
    try:
        user_id = auth.verify_session_token(token)
    except AuthError:
        raise HTTPException(status_code=401, detail="Not authenticated") from None
    try:
        session_user_id = await repository.find_session(auth.hash_token(token))
    except ValueError:
        raise HTTPException(status_code=503, detail="Database unavailable") from None
    if session_user_id != user_id:
        raise HTTPException(status_code=401, detail="Not authenticated")
    user = await repository.get_user(user_id)
    if user is None:
        raise HTTPException(status_code=401, detail="Not authenticated")
    return user


def get_extraction_service() -> ExtractionService:
    return ExtractionService(llm=get_llm_adapter())


def get_policy_extraction_service() -> PolicyExtractionService:
    return PolicyExtractionService(llm=get_llm_adapter())


def get_method_draft_extraction_service() -> MethodDraftExtractionService:
    return MethodDraftExtractionService(llm=get_llm_adapter())


def get_document_draft_extraction_service() -> DocumentDraftExtractionService:
    return DocumentDraftExtractionService(llm=get_llm_adapter())


def get_regulation_draft_extraction_service() -> RegulationDraftExtractionService:
    return RegulationDraftExtractionService(llm=get_llm_adapter())


def get_extract_estimate_service() -> ExtractEstimateService:
    return ExtractEstimateService()


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
