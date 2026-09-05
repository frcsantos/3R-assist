from fastapi import APIRouter, Depends
from fastapi.responses import JSONResponse

from app.adapters.llm import ExtractionError
from app.api.deps import get_extraction_service, require_admin_token
from app.api.errors import ErrorEnvelope, error_response
from app.models.protocol import AnalyzeRequest, AnalyzeResponse
from app.services.extraction import ExtractionService

router = APIRouter(tags=["analysis"], dependencies=[Depends(require_admin_token)])


@router.post(
    "/analyze",
    response_model=AnalyzeResponse,
    responses={422: {"model": ErrorEnvelope}},
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
