"""Async LLM helper for pubmed services.

LLMAdapter.call() is synchronous (blocking HTTP to Ollama). This module
provides async_call() so pubmed async code can await it without blocking
the event loop, keeping app/adapters/llm.py free of pubmed-specific changes.
"""
from __future__ import annotations

import asyncio

from app.adapters.llm import LLMAdapter


async def async_call(
    llm: LLMAdapter,
    prompt: str,
    *,
    max_tokens: int,
    json_mode: bool = False,
) -> str | None:
    """Run llm.call() in a thread-pool executor so it can be awaited."""
    loop = asyncio.get_event_loop()
    return await loop.run_in_executor(
        None,
        lambda: llm.call(prompt, max_tokens=max_tokens, json_mode=json_mode),
    )
