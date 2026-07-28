from typing import Literal

from fastapi import APIRouter, Depends, Query
from fastapi.responses import JSONResponse

from app.api.deps import get_document_repository
from app.api.errors import error_response
from app.config import get_settings
from app.models.catalogue import DocumentsCatalogueResponse
from app.repositories.documents import DocumentRepository

DocumentCategory = Literal["method_protocol", "guideline", "regulation"]

router = APIRouter(tags=["documents"])


@router.get("/documents", response_model=DocumentsCatalogueResponse)
async def list_documents(
    category: list[DocumentCategory] | None = Query(default=None),
    repository: DocumentRepository = Depends(get_document_repository),
) -> DocumentsCatalogueResponse | JSONResponse:
    if not get_settings().database_url:
        return error_response(
            status_code=503,
            code="DATABASE_UNAVAILABLE",
            message="Document database is not configured.",
        )

    documents = await repository.list_all(categories=category)
    return DocumentsCatalogueResponse(documents=documents)
