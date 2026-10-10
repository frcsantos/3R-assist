import asyncio
import json
import logging
import traceback

from fastapi import APIRouter, Depends
from fastapi.responses import JSONResponse, StreamingResponse

logger = logging.getLogger(__name__)
from app.api.errors import ErrorEnvelope, error_response
from pubmed.api.deps import get_pubmed_analysis_service
from pubmed.models.analysis import PubMedAnalysisResponse, PubMedAnalyzeRequest
from pubmed.services.analysis import PubMedAnalysisService

router = APIRouter(prefix="/pubmed", tags=["pubmed"])

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


@router.post(
    "/analyze-stream",
    summary="Streaming version of /analyze — sends SSE heartbeats to prevent proxy timeouts",
    description=(
        "Identical logic to /analyze but returns a text/event-stream response. "
        "Sends `event: ping` every 10 s while the LLM is processing so that "
        "Cloudflare (524) and other reverse-proxies do not close the connection. "
        "Ends with `event: result` carrying the full PubMedAnalysisResponse JSON, "
        "or `event: error` on failure."
    ),
)
async def analyze_protocol_stream(
    payload: PubMedAnalyzeRequest,
    service: PubMedAnalysisService = Depends(get_pubmed_analysis_service),
) -> StreamingResponse:
    try:
        await asyncio.wait_for(_analysis_semaphore.acquire(), timeout=0.1)
    except asyncio.TimeoutError:
        async def _busy():
            yield 'event: error\ndata: {"code":"SERVER_BUSY","message":"Server is busy. Please try again in a moment."}\n\n'
        return StreamingResponse(_busy(), media_type="text/event-stream")

    async def generate():
        task = None
        try:
            done = asyncio.Event()
            holder: dict = {}

            async def _run():
                try:
                    holder["result"] = await service.analyze(payload)
                except Exception as exc:
                    tb = traceback.format_exc()
                    logger.error("analyze_stream error: %s\n%s", exc, tb)
                    holder["error"] = str(exc)
                finally:
                    done.set()

            task = asyncio.create_task(_run())

            # Heartbeat loop — keeps Cloudflare / nginx alive while LLM processes
            while True:
                try:
                    await asyncio.wait_for(done.wait(), timeout=10.0)
                    break
                except asyncio.TimeoutError:
                    yield "event: ping\ndata: {}\n\n"

            if "error" in holder:
                yield f'event: error\ndata: {json.dumps({"message": holder["error"]})}\n\n'
            else:
                yield f"event: result\ndata: {holder['result'].model_dump_json()}\n\n"

        finally:
            if task and not task.done():
                task.cancel()
            _analysis_semaphore.release()

    return StreamingResponse(generate(), media_type="text/event-stream")


@router.get(
    "/status",
    summary="Knowledge base record count",
)
async def knowledge_base_status(
    service: PubMedAnalysisService = Depends(get_pubmed_analysis_service),
) -> dict:
    count = await service._retrieval._repository.count()
    return {"pubmed_records_indexed": count}
