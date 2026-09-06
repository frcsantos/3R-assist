from __future__ import annotations

from app.adapters.embedder import EmbedderAdapter
from app.adapters.llm import ExtractionError, LLMAdapter
from app.models.protocol import ProtocolParameters
from app.services.extraction import ExtractionService
from pubmed.db.repository import PubMedRepository
from pubmed.models.analysis import PubMedAnalysisResponse, PubMedAnalyzeRequest
from pubmed.services.retrieval import PubMedRetrievalService


class PubMedAnalysisService:
    def __init__(
        self,
        llm: LLMAdapter,
        embedder: EmbedderAdapter,
        repository: PubMedRepository,
        extraction: ExtractionService,
    ) -> None:
        self._retrieval = PubMedRetrievalService(
            repository=repository, embedder=embedder, llm=llm
        )
        self._extraction = extraction

    async def analyze(self, request: PubMedAnalyzeRequest) -> PubMedAnalysisResponse:
        params = request.params or self._extract_params(request.protocol_text)

        recommendations, endpoint_hypothesis, total = (
            await self._retrieval.search(params, request.protocol_text)
        )

        summary, citations = self._retrieval.generate_summary(params, recommendations)

        return PubMedAnalysisResponse(
            necessity=None,
            endpoint_hypothesis=endpoint_hypothesis,
            recommendations=recommendations,
            summary=summary,
            citations=citations,
            no_literature_found=len(recommendations) == 0,
            total_candidates_searched=total,
        )

    def _extract_params(self, protocol_text: str) -> ProtocolParameters:
        result = self._extraction.extract(protocol_text)
        if isinstance(result, ExtractionError):
            return ProtocolParameters()
        return result.params
