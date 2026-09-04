from fastapi import APIRouter, Depends
from fastapi.responses import JSONResponse

from app.api.deps import get_feedback_repository
from app.api.errors import error_response
from app.config import get_settings
from app.models.feedback import Feedback, FeedbackCreate
from app.repositories.feedback import FeedbackRepository

router = APIRouter(tags=["feedback"])


@router.post("/feedback", response_model=Feedback, status_code=201)
async def create_feedback(
    payload: FeedbackCreate,
    repository: FeedbackRepository = Depends(get_feedback_repository),
) -> Feedback | JSONResponse:
    if not get_settings().database_url:
        return error_response(
            status_code=503,
            code="DATABASE_UNAVAILABLE",
            message="Feedback database is not configured.",
        )

    return await repository.create(payload)
