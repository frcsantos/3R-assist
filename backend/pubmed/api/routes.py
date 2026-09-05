import asyncio
import logging
import traceback

from fastapi import APIRouter, Depends
from fastapi.responses import JSONResponse

from app.api.deps import require_admin_token

logger = logging.getLogger(__name__)
from app.api.errors import ErrorEnvelope, error_response
from pubmed.api.deps import get_pubmed_analysis_service
from pubmed.models.analysis import PubMedAnalysisResponse, PubMedAnalyzeRequest
from pubmed.services.analysis import PubMedAnalysisService

router = APIRouter(prefix="/pubmed", tags=["pubmed"], dependencies=[Depends(require_admin_token)])

# Limit concurrent analyses to prevent RAM exhaustion under load.
# Extra requests get an immediate 503 rather than queuing indefinitely.
_analysis_semaphore = asyncio.Semaphore(1)


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
        await asyncio.wait_for(_analysis_semaphore.acquire(), timeout=0.1)
    except asyncio.TimeoutError:
        return error_response(
            status_code=503,
            code="SERVER_BUSY",
            message="Server is busy processing other requests. Please try again in a moment.",
        )
    try:
        return await service.analyze(payload)
    except Exception as exc:
        tb = traceback.format_exc()
        logger.error("analyze_protocol error: %s\n%s", exc, tb)
        try:
            with open("/tmp/pubmed_error.log", "w") as _f:
                _f.write(tb)
        except Exception:
            pass
        return error_response(
            status_code=422,
            code="PUBMED_ANALYSIS_FAILED",
            message="PubMed analysis failed. Please try again.",
        )
    finally:
        _analysis_semaphore.release()


@router.get(
    "/status",
    summary="Knowledge base record count",
)
async def knowledge_base_status(
    service: PubMedAnalysisService = Depends(get_pubmed_analysis_service),
) -> dict:
    count = await service._retrieval._repository.count()
    return {"pubmed_records_indexed": count}
