from fastapi import APIRouter, Depends
from fastapi.responses import JSONResponse

from app.adapters.llm import ExtractionError
from app.api.deps import get_extraction_service
from app.api.errors import ErrorEnvelope, error_response
from app.models.protocol import AnalyzeRequest, AnalyzeResponse
from app.services.extraction import ExtractionService
from app.services.vocabulary import ensure_applications_loaded

router = APIRouter(tags=["analysis"])


@router.post(
    "/analyze",
    response_model=AnalyzeResponse,
    responses={422: {"model": ErrorEnvelope}},
    dependencies=[Depends(ensure_applications_loaded)],
)
async def analyze_protocol(
    payload: AnalyzeRequest,
    extraction: ExtractionService = Depends(get_extraction_service),
) -> AnalyzeResponse | JSONResponse:
    result = extraction.extract(payload.protocol_text)
    if isinstance(result, ExtractionError):
        return error_response(
            status_code=422,
            code=result.code,
            message=result.message,
        )

    return result
