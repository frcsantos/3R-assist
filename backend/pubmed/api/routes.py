import asyncio
import json
import logging
import traceback
from dataclasses import dataclass, field

from fastapi import APIRouter, Depends
from fastapi.responses import JSONResponse, StreamingResponse

logger = logging.getLogger(__name__)
from app.api.errors import ErrorEnvelope, error_response
from pubmed.api.deps import get_pubmed_analysis_service
from pubmed.models.analysis import PubMedAnalysisResponse, PubMedAnalyzeRequest
from pubmed.services.analysis import PubMedAnalysisService

router = APIRouter(prefix="/pubmed", tags=["pubmed"])

# ── Queue manager ─────────────────────────────────────────────────────────────
# One analysis runs at a time. Subsequent requests queue (up to _MAX_QUEUE)
# and are notified via SSE queue events instead of receiving a 503.

_MAX_CONCURRENT = 1
_MAX_QUEUE = 10


@dataclass
class _Waiter:
    ready: asyncio.Event = field(default_factory=asyncio.Event)


_active: int = 0
_queue: list[_Waiter] = []
_lock = asyncio.Lock()


async def _enqueue() -> tuple[int, "_Waiter | None"]:
    """Attempt to acquire a slot.

    Returns (position, waiter):
      position == 0           — running immediately, waiter is None
      position in 1..MAX_QUEUE — queued at that position
      position == -1          — queue full, reject
    """
    global _active
    async with _lock:
        if _active < _MAX_CONCURRENT:
            _active += 1
            return 0, None
        if len(_queue) >= _MAX_QUEUE:
            return -1, None
        waiter = _Waiter()
        _queue.append(waiter)
        return len(_queue), waiter


async def _release(started: bool, waiter: "_Waiter | None") -> None:
    """Release the slot or remove a queued-but-not-yet-started waiter."""
    global _active
    async with _lock:
        if waiter is not None and not started:
            # Client disconnected while still in queue — remove without waking anyone
            try:
                _queue.remove(waiter)
            except ValueError:
                pass
            return
        # Slot was held (either started immediately or waiter was promoted) — hand off
        if _queue:
            next_waiter = _queue.pop(0)
            next_waiter.ready.set()
        else:
            _active -= 1


def _position_of(waiter: "_Waiter") -> int:
    try:
        return _queue.index(waiter) + 1
    except ValueError:
        return 0


# ── Routes ────────────────────────────────────────────────────────────────────

@router.post(
    "/analyze",
    response_model=PubMedAnalysisResponse,
    responses={422: {"model": ErrorEnvelope}},
    summary="Assess animal-use necessity and retrieve literature-backed alternatives",
)
async def analyze_protocol(
    payload: PubMedAnalyzeRequest,
    service: PubMedAnalysisService = Depends(get_pubmed_analysis_service),
) -> PubMedAnalysisResponse | JSONResponse:
    position, waiter = await _enqueue()
    if position == -1:
        return error_response(
            status_code=503,
            code="QUEUE_FULL",
            message="Too many requests queued. Please try again in a moment.",
        )
    started = position == 0
    if waiter is not None:
        await waiter.ready.wait()
        started = True
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
        await _release(started, waiter)


@router.post(
    "/analyze-stream",
    summary="Streaming version of /analyze — SSE heartbeats + queue position updates",
)
async def analyze_protocol_stream(
    payload: PubMedAnalyzeRequest,
    service: PubMedAnalysisService = Depends(get_pubmed_analysis_service),
) -> StreamingResponse:
    position, waiter = await _enqueue()

    if position == -1:
        async def _full():
            yield 'event: error\ndata: {"code":"QUEUE_FULL","message":"Too many requests queued. Please try again later."}\n\n'
        return StreamingResponse(_full(), media_type="text/event-stream")

    async def generate():
        started = position == 0
        task = None
        try:
            # ── Queue wait phase ──────────────────────────────────────────────
            if waiter is not None:
                while not waiter.ready.is_set():
                    pos = _position_of(waiter)
                    yield f'event: queue\ndata: {{"position": {pos}}}\n\n'
                    try:
                        await asyncio.wait_for(waiter.ready.wait(), timeout=5.0)
                        break
                    except asyncio.TimeoutError:
                        pass
                started = True
                yield 'event: queue\ndata: {"position": 0}\n\n'

            # ── Analysis phase ────────────────────────────────────────────────
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
            await _release(started, waiter)

    return StreamingResponse(generate(), media_type="text/event-stream")


@router.get("/status", summary="Knowledge base record count")
async def knowledge_base_status(
    service: PubMedAnalysisService = Depends(get_pubmed_analysis_service),
) -> dict:
    count = await service._retrieval._repository.count()
    return {"pubmed_records_indexed": count}
