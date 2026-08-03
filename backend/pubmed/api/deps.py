from functools import lru_cache

from app.api.deps import get_embedder, get_extraction_service, get_llm_adapter
from pubmed.db.repository import PubMedRepository
from pubmed.services.analysis import PubMedAnalysisService


@lru_cache
def get_pubmed_repository() -> PubMedRepository:
    return PubMedRepository()


def get_pubmed_analysis_service() -> PubMedAnalysisService:
    return PubMedAnalysisService(
        llm=get_llm_adapter(),
        embedder=get_embedder(),
        repository=get_pubmed_repository(),
        extraction=get_extraction_service(),
    )
