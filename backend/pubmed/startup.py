"""Pubmed module startup — pre-loads embedder and Ollama into memory."""
from __future__ import annotations

import asyncio
import logging

logger = logging.getLogger(__name__)


async def warmup() -> None:
    loop = asyncio.get_event_loop()

    from app.api.deps import get_embedder
    try:
        await loop.run_in_executor(None, lambda: get_embedder().embed("warmup"))
        logger.info("Embedder warmed up.")
    except Exception as e:
        logger.warning("Embedder warmup failed: %s", e)

    from app.config import get_settings
    if get_settings().ollama_model:
        from app.adapters.llm import OllamaLLMAdapter
        _ollama = OllamaLLMAdapter(model=get_settings().ollama_model)
        try:
            await loop.run_in_executor(None, lambda: _ollama.call("warmup", max_tokens=1))
            logger.info("Ollama warmed up.")
        except Exception as e:
            logger.warning("Ollama warmup failed: %s", e)
