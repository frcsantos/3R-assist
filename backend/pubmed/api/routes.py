from fastapi import APIRouter, Depends
from fastapi.responses import JSONResponse

from app.api.errors import ErrorEnvelope, error_response
from pubmed.api.deps import get_pubmed_analysis_service
from pubmed.models.analysis import PubMedAnalysisResponse, PubMedAnalyzeRequest
from pubmed.services.analysis import PubMedAnalysisService

router = APIRouter(prefix="/pubmed", tags=["pubmed"])


@router.post(
    "/analyze",
    response_model=PubMedAnalysisResponse,
    responses={422: {"model": ErrorEnvelope}},
    summary="Assess animal-use necessity and retrieve literature-backed alternatives",
    description=(
        "Runs two parallel searches against the PubMed knowledge base: "
        "(A) a neutral endpoint/hypothesis search and "
        "(B) LLM-reconstructed alternative method queries weighted by 3R class. "
        "Results are merged, ranked with Replace > Reduce > Refine weighting, "
        "and filtered to only include actionable alternatives."
    ),
)
async def analyze_protocol(
    payload: PubMedAnalyzeRequest,
    service: PubMedAnalysisService = Depends(get_pubmed_analysis_service),
) -> PubMedAnalysisResponse | JSONResponse:
    try:
        return await service.analyze(payload)
    except Exception as exc:
        return error_response(
            status_code=422,
            code="PUBMED_ANALYSIS_FAILED",
            message=str(exc),
        )


@router.get(
    "/status",
    summary="Knowledge base record count",
)
async def knowledge_base_status(
    service: PubMedAnalysisService = Depends(get_pubmed_analysis_service),
) -> dict:
    count = await service._retrieval._repository.count()
    return {"pubmed_records_indexed": count}
