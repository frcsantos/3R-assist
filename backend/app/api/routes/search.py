from fastapi import APIRouter, Depends
from fastapi.responses import JSONResponse

from app.api.deps import get_retrieval_service
from app.api.errors import error_response
from app.config import get_settings
from app.models.jurisdiction import jurisdiction_matches
from app.models.protocol import SearchFilters, SearchRequest, SearchResponse
from app.models.recommendation import Recommendation
from app.services.retrieval import RetrievalService

router = APIRouter(tags=["search"])


def _matches_three_r_filter(recommendation: Recommendation, three_r_class: str) -> bool:
    return recommendation.method.has_three_r(three_r_class)


def _matches_jurisdiction_filter(
    recommendation: Recommendation,
    jurisdiction: str,
) -> bool:
    return any(
        jurisdiction_matches(context.jurisdiction, jurisdiction)
        for context in recommendation.regulatory_contexts
    )


def _apply_filters(
    recommendations: list[Recommendation],
    filters: SearchFilters | None,
) -> list[Recommendation]:
    if filters is None:
        return recommendations

    filtered = recommendations
    if filters.three_r_class is not None:
        filtered = [
            item
            for item in filtered
            if _matches_three_r_filter(item, filters.three_r_class)
        ]
    if filters.jurisdiction is not None:
        filtered = [
            item
            for item in filtered
            if _matches_jurisdiction_filter(item, filters.jurisdiction)
        ]
    if filters.endpoint is not None:
        filtered = [
            item
            for item in filtered
            if item.method.endpoint_category == filters.endpoint
        ]
    return filtered


@router.post("/search", response_model=SearchResponse)
async def search_methods(
    payload: SearchRequest,
    retrieval: RetrievalService = Depends(get_retrieval_service),
) -> SearchResponse | JSONResponse:
    if not get_settings().database_url:
        return error_response(
            status_code=503,
            code="DATABASE_UNAVAILABLE",
            message="Method database is not configured.",
        )

    recommendations, filter_relaxation = await retrieval.search(
        payload.params,
        lang=payload.lang,
    )
    results = _apply_filters(recommendations, payload.filters)
    return SearchResponse(
        query_id=None,
        results=results,
        filter_relaxation=filter_relaxation,
    )
