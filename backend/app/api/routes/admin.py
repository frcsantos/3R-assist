from fastapi import APIRouter, Depends, File, Query, UploadFile
from fastapi.responses import JSONResponse

from app.adapters.llm import ExtractionError
from app.api.deps import (
    get_admin_repository,
    get_document_draft_extraction_service,
    get_extract_estimate_service,
    get_method_draft_extraction_service,
    get_policy_document_match_service,
    get_policy_extraction_service,
    get_policy_method_match_service,
    get_regulation_draft_extraction_service,
)
from app.api.errors import ErrorEnvelope, error_response
from app.config import get_settings
from app.models.admin import (
    AdminCellUpdateRequest,
    AdminCellUpdateResponse,
    AdminColumnCommentUpdateRequest,
    AdminColumnCommentUpdateResponse,
    AdminRowInsertRequest,
    AdminRowInsertResponse,
    AdminRowsDeleteRequest,
    AdminRowsDeleteResponse,
    AdminSettingsResponse,
    AdminTableDataResponse,
    AdminTablesResponse,
)
from app.models.document_draft import (
    DocumentDraftExtractRequest,
    DocumentDraftExtractResponse,
)
from app.models.extract_estimate import (
    ExtractEstimateRequest,
    ExtractEstimateResponse,
    ExtractResolveRequest,
    ExtractResolveResponse,
)
from app.models.extract_upload import ExtractUploadResponse
from app.models.method_draft import (
    MethodDraftExtractRequest,
    MethodDraftExtractResponse,
)
from app.models.regulation_draft import (
    RegulationDraftExtractRequest,
    RegulationDraftExtractResponse,
)
from app.models.policy import (
    PolicyDocumentMatchRequest,
    PolicyDocumentMatchResponse,
    PolicyExtractRequest,
    PolicyExtractResponse,
    PolicyMethodMatchRequest,
    PolicyMethodMatchResponse,
)
from app.repositories.admin import AdminRepository
from app.services.document_draft_extraction import DocumentDraftExtractionService
from app.services.extract_estimate import ExtractEstimateService
from app.services.file_text import FileTextError, extract_text_from_upload
from app.services.method_draft_extraction import MethodDraftExtractionService
from app.services.regulation_draft_extraction import RegulationDraftExtractionService
from app.services.policy_document_match import PolicyDocumentMatchService
from app.services.policy_extraction import PolicyExtractionService
from app.services.policy_method_match import PolicyMethodMatchService
from app.services.url_text import UrlTextError, resolve_extraction_source

router = APIRouter(prefix="/admin", tags=["admin"])


@router.get("/settings", response_model=AdminSettingsResponse)
async def get_admin_settings() -> AdminSettingsResponse:
    settings = get_settings()
    return AdminSettingsResponse(
        app_env=settings.app_env,
        llm_model=settings.resolved_llm_model,
    )


@router.get("/tables", response_model=AdminTablesResponse)
async def list_tables(
    repository: AdminRepository = Depends(get_admin_repository),
) -> AdminTablesResponse | JSONResponse:
    try:
        tables = await repository.list_tables()
    except ValueError as exc:
        return error_response(
            status_code=503,
            code="DATABASE_UNAVAILABLE",
            message=str(exc),
        )
    except Exception as exc:
        return error_response(
            status_code=503,
            code="DATABASE_UNAVAILABLE",
            message="Could not load database tables.",
            detail={"type": type(exc).__name__, "reason": str(exc)},
        )
    return AdminTablesResponse(tables=tables)


@router.get(
    "/tables/{table_name}",
    response_model=AdminTableDataResponse,
    responses={404: {"model": ErrorEnvelope}, 503: {"model": ErrorEnvelope}},
)
async def get_table_data(
    table_name: str,
    limit: int = Query(default=100, ge=1, le=500),
    offset: int = Query(default=0, ge=0),
    sort_by: str | None = Query(default=None, min_length=1, max_length=63),
    sort_dir: str = Query(default="asc"),
    repository: AdminRepository = Depends(get_admin_repository),
) -> AdminTableDataResponse | JSONResponse:
    try:
        payload = await repository.fetch_table(
            table_name,
            limit=limit,
            offset=offset,
            sort_by=sort_by,
            sort_dir=sort_dir,
        )
    except LookupError:
        return error_response(
            status_code=404,
            code="TABLE_NOT_FOUND",
            message=f"Table '{table_name}' was not found.",
        )
    except ValueError as exc:
        return error_response(
            status_code=400,
            code="INVALID_TABLE",
            message=str(exc),
        )
    except Exception as exc:
        return error_response(
            status_code=503,
            code="DATABASE_UNAVAILABLE",
            message="Could not load table data.",
            detail={"type": type(exc).__name__, "reason": str(exc)},
        )
    return AdminTableDataResponse(**payload)


@router.post(
    "/tables/{table_name}",
    response_model=AdminRowInsertResponse,
    responses={
        400: {"model": ErrorEnvelope},
        404: {"model": ErrorEnvelope},
        503: {"model": ErrorEnvelope},
    },
)
async def insert_table_row(
    table_name: str,
    body: AdminRowInsertRequest,
    repository: AdminRepository = Depends(get_admin_repository),
) -> AdminRowInsertResponse | JSONResponse:
    try:
        payload = await repository.insert_row(
            table_name,
            values=body.values,
        )
    except LookupError:
        return error_response(
            status_code=404,
            code="TABLE_NOT_FOUND",
            message=f"Table '{table_name}' was not found.",
        )
    except ValueError as exc:
        return error_response(
            status_code=400,
            code="INVALID_INSERT",
            message=str(exc),
        )
    except Exception as exc:
        return error_response(
            status_code=503,
            code="DATABASE_UNAVAILABLE",
            message=(
                f"Could not insert table row: {type(exc).__name__}: {exc}"
            ),
            detail={"type": type(exc).__name__, "reason": str(exc)},
        )
    return AdminRowInsertResponse(**payload)


@router.patch(
    "/tables/{table_name}",
    response_model=AdminCellUpdateResponse,
    responses={
        400: {"model": ErrorEnvelope},
        404: {"model": ErrorEnvelope},
        503: {"model": ErrorEnvelope},
    },
)
async def update_table_cell(
    table_name: str,
    body: AdminCellUpdateRequest,
    repository: AdminRepository = Depends(get_admin_repository),
) -> AdminCellUpdateResponse | JSONResponse:
    try:
        payload = await repository.update_cell(
            table_name,
            primary_key=body.primary_key,
            column=body.column,
            value=body.value,
        )
    except LookupError as exc:
        if str(exc) == "row":
            return error_response(
                status_code=404,
                code="ROW_NOT_FOUND",
                message="Row was not found.",
            )
        return error_response(
            status_code=404,
            code="TABLE_NOT_FOUND",
            message=f"Table '{table_name}' was not found.",
        )
    except ValueError as exc:
        return error_response(
            status_code=400,
            code="INVALID_UPDATE",
            message=str(exc),
        )
    except Exception as exc:
        return error_response(
            status_code=503,
            code="DATABASE_UNAVAILABLE",
            message=(
                f"Could not update table data: {type(exc).__name__}: {exc}"
            ),
            detail={"type": type(exc).__name__, "reason": str(exc)},
        )
    return AdminCellUpdateResponse(**payload)


@router.delete(
    "/tables/{table_name}",
    response_model=AdminRowsDeleteResponse,
    responses={
        400: {"model": ErrorEnvelope},
        404: {"model": ErrorEnvelope},
        503: {"model": ErrorEnvelope},
    },
)
async def delete_table_rows(
    table_name: str,
    body: AdminRowsDeleteRequest,
    repository: AdminRepository = Depends(get_admin_repository),
) -> AdminRowsDeleteResponse | JSONResponse:
    try:
        payload = await repository.delete_rows(
            table_name,
            rows=body.rows,
        )
    except LookupError:
        return error_response(
            status_code=404,
            code="TABLE_NOT_FOUND",
            message=f"Table '{table_name}' was not found.",
        )
    except ValueError as exc:
        return error_response(
            status_code=400,
            code="INVALID_DELETE",
            message=str(exc),
        )
    except Exception as exc:
        return error_response(
            status_code=503,
            code="DATABASE_UNAVAILABLE",
            message=(
                f"Could not delete table rows: {type(exc).__name__}: {exc}"
            ),
            detail={"type": type(exc).__name__, "reason": str(exc)},
        )
    return AdminRowsDeleteResponse(**payload)


@router.patch(
    "/tables/{table_name}/columns/{column_name}/comment",
    response_model=AdminColumnCommentUpdateResponse,
    responses={
        400: {"model": ErrorEnvelope},
        404: {"model": ErrorEnvelope},
        503: {"model": ErrorEnvelope},
    },
)
async def update_column_comment(
    table_name: str,
    column_name: str,
    body: AdminColumnCommentUpdateRequest,
    repository: AdminRepository = Depends(get_admin_repository),
) -> AdminColumnCommentUpdateResponse | JSONResponse:
    try:
        payload = await repository.update_column_comment(
            table_name,
            column_name,
            comment=body.comment,
        )
    except LookupError:
        return error_response(
            status_code=404,
            code="TABLE_NOT_FOUND",
            message=f"Table '{table_name}' was not found.",
        )
    except ValueError as exc:
        return error_response(
            status_code=400,
            code="INVALID_COMMENT",
            message=str(exc),
        )
    except Exception as exc:
        return error_response(
            status_code=503,
            code="DATABASE_UNAVAILABLE",
            message=(
                f"Could not update column comment: {type(exc).__name__}: {exc}"
            ),
            detail={"type": type(exc).__name__, "reason": str(exc)},
        )
    return AdminColumnCommentUpdateResponse(**payload)


@router.post(
    "/extract/resolve",
    response_model=ExtractResolveResponse,
    responses={422: {"model": ErrorEnvelope}},
)
async def resolve_extract_source(
    payload: ExtractResolveRequest,
) -> ExtractResolveResponse | JSONResponse:
    try:
        source_text, source_url = await resolve_extraction_source(payload.text)
    except UrlTextError as exc:
        return error_response(
            status_code=422,
            code=exc.code,
            message=exc.message,
        )
    return ExtractResolveResponse(
        text=source_text,
        source_url=source_url,
        fetched=source_url is not None,
    )


@router.post(
    "/extract/upload",
    response_model=ExtractUploadResponse,
    responses={422: {"model": ErrorEnvelope}},
)
async def upload_extract_source(
    file: UploadFile = File(...),
) -> ExtractUploadResponse | JSONResponse:
    raw = await file.read()
    try:
        text = extract_text_from_upload(
            filename=file.filename,
            content_type=file.content_type,
            raw=raw,
        )
    except FileTextError as exc:
        return error_response(
            status_code=422,
            code=exc.code,
            message=exc.message,
        )

    filename = (file.filename or "document").strip() or "document"
    return ExtractUploadResponse(
        filename=filename,
        text=text,
        char_count=len(text),
    )


@router.post(
    "/extract/estimate",
    response_model=ExtractEstimateResponse,
    responses={422: {"model": ErrorEnvelope}},
)
async def estimate_extract(
    payload: ExtractEstimateRequest,
    estimation: ExtractEstimateService = Depends(get_extract_estimate_service),
) -> ExtractEstimateResponse | JSONResponse:
    try:
        source_text, fetched_url = await resolve_extraction_source(payload.text)
    except UrlTextError as exc:
        return error_response(
            status_code=422,
            code=exc.code,
            message=exc.message,
        )

    source_url = payload.source_url or fetched_url
    return estimation.estimate(
        source_text,
        mode=payload.mode,
        category_hint=payload.category_hint,
        source_url=source_url,
    )


@router.post(
    "/extract/policy",
    response_model=PolicyExtractResponse,
    responses={422: {"model": ErrorEnvelope}},
)
async def extract_policy(
    payload: PolicyExtractRequest,
    extraction: PolicyExtractionService = Depends(get_policy_extraction_service),
) -> PolicyExtractResponse | JSONResponse:
    try:
        source_text, fetched_url = await resolve_extraction_source(payload.text)
    except UrlTextError as exc:
        return error_response(
            status_code=422,
            code=exc.code,
            message=exc.message,
        )

    source_url = payload.source_url or fetched_url
    result = extraction.extract(source_text, source_url=source_url)
    if isinstance(result, ExtractionError):
        return error_response(
            status_code=422,
            code=result.code,
            message=result.message,
        )
    return result


@router.post(
    "/extract/document-draft",
    response_model=DocumentDraftExtractResponse,
    responses={422: {"model": ErrorEnvelope}},
)
async def extract_document_draft(
    payload: DocumentDraftExtractRequest,
    extraction: DocumentDraftExtractionService = Depends(
        get_document_draft_extraction_service
    ),
) -> DocumentDraftExtractResponse | JSONResponse:
    try:
        source_text, fetched_url = await resolve_extraction_source(payload.text)
    except UrlTextError as exc:
        return error_response(
            status_code=422,
            code=exc.code,
            message=exc.message,
        )

    source_url = payload.source_url or fetched_url
    result = extraction.extract(
        source_text,
        category_hint=payload.category_hint,
        source_url=source_url,
    )
    if isinstance(result, ExtractionError):
        return error_response(
            status_code=422,
            code=result.code,
            message=result.message,
        )
    return result


@router.post(
    "/extract/method-draft",
    response_model=MethodDraftExtractResponse,
    responses={422: {"model": ErrorEnvelope}},
)
async def extract_method_draft(
    payload: MethodDraftExtractRequest,
    extraction: MethodDraftExtractionService = Depends(
        get_method_draft_extraction_service
    ),
) -> MethodDraftExtractResponse | JSONResponse:
    result = extraction.extract(payload.text)
    if isinstance(result, ExtractionError):
        return error_response(
            status_code=422,
            code=result.code,
            message=result.message,
        )
    return result


@router.post(
    "/extract/regulation-draft",
    response_model=RegulationDraftExtractResponse,
    responses={422: {"model": ErrorEnvelope}},
)
async def extract_regulation_draft(
    payload: RegulationDraftExtractRequest,
    extraction: RegulationDraftExtractionService = Depends(
        get_regulation_draft_extraction_service
    ),
) -> RegulationDraftExtractResponse | JSONResponse:
    try:
        source_text, fetched_url = await resolve_extraction_source(payload.text)
    except UrlTextError as exc:
        return error_response(
            status_code=422,
            code=exc.code,
            message=exc.message,
        )

    source_url = payload.source_url or fetched_url
    result = extraction.extract(source_text, source_url=source_url)
    if isinstance(result, ExtractionError):
        return error_response(
            status_code=422,
            code=result.code,
            message=result.message,
        )
    return result


@router.post(
    "/extract/policy/match-method",
    response_model=PolicyMethodMatchResponse,
    response_model_exclude={
        "matches": {"__all__": {"method": {"embedding_json"}}},
    },
    responses={503: {"model": ErrorEnvelope}},
)
async def match_policy_method(
    payload: PolicyMethodMatchRequest,
    matching: PolicyMethodMatchService = Depends(get_policy_method_match_service),
) -> PolicyMethodMatchResponse | JSONResponse:
    try:
        return await matching.match(payload)
    except Exception as exc:
        return error_response(
            status_code=503,
            code="METHOD_MATCH_FAILED",
            message=(
                "Could not search for matching methods in the database. "
                "Try again, or check that curated methods have valid metadata."
            ),
            detail={"type": type(exc).__name__, "reason": str(exc)},
        )


@router.post(
    "/extract/policy/match-document",
    response_model=PolicyDocumentMatchResponse,
    responses={503: {"model": ErrorEnvelope}},
)
async def match_policy_document(
    payload: PolicyDocumentMatchRequest,
    matching: PolicyDocumentMatchService = Depends(
        get_policy_document_match_service
    ),
) -> PolicyDocumentMatchResponse | JSONResponse:
    try:
        return await matching.match(payload)
    except Exception as exc:
        return error_response(
            status_code=503,
            code="DOCUMENT_MATCH_FAILED",
            message=(
                "Could not search for matching documents in the database. "
                "Try again, or check that curated documents have valid metadata."
            ),
            detail={"type": type(exc).__name__, "reason": str(exc)},
        )
