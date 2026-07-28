from fastapi import APIRouter, Depends, Query
from fastapi.responses import JSONResponse

from app.api.deps import get_method_repository
from app.api.errors import error_response
from app.config import get_settings
from app.models.catalogue import MethodCatalogueItem, MethodsCatalogueResponse
from app.repositories.methods import MethodRepository

router = APIRouter(tags=["methods"])


@router.get(
    "/methods",
    response_model=MethodsCatalogueResponse,
    response_model_exclude={
        "methods": {
            "__all__": {
                "method": {"embedding_json", "text_for_embedding"},
            }
        }
    },
)
async def list_methods(
    lang: str | None = Query(default=None),
    repository: MethodRepository = Depends(get_method_repository),
) -> MethodsCatalogueResponse | JSONResponse:
    if not get_settings().database_url:
        return error_response(
            status_code=503,
            code="DATABASE_UNAVAILABLE",
            message="Method database is not configured.",
        )

    methods, contexts_by_method = await repository.list_with_contexts(
        active_only=False,
    )
    items = [
        MethodCatalogueItem(
            method=method,
            regulatory_contexts=contexts_by_method.get(method.id, []),
        )
        for method in methods
    ]
    items.sort(key=lambda item: item.method.name.pick(lang).casefold())
    return MethodsCatalogueResponse(methods=items)
