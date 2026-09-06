"""Estimate extraction LLM cost with a fast local approximation."""

from __future__ import annotations

import json
import logging
from functools import lru_cache
from importlib import util as importlib_util
from pathlib import Path

from app.config import get_settings
from app.models.extract_estimate import ExtractEstimateResponse, ExtractMode
from app.prompts.document_draft_extraction import build_document_draft_extraction_prompt
from app.prompts.policy_extraction import build_policy_extraction_prompt
from app.services.language import detect_lang, language_label

logger = logging.getLogger(__name__)

# Expected completion size for cost estimates (not the API max_tokens ceiling).
# Using max_tokens made estimates look flat: output dominated cost and the
# displayed token total barely moved with source text length.
_POLICY_EXPECTED_OUTPUT_TOKENS = 1200
_DOCUMENT_EXPECTED_OUTPUT_TOKENS = 600


def _approx_tokens(text: str) -> int:
    """Rough token count (~4 chars/token). Avoids LiteLLM token_counter (very slow)."""
    return max(1, len(text) // 4)


@lru_cache(maxsize=1)
def _model_price_map() -> dict:
    """Load LiteLLM's on-disk price table without importing the package (cold import is slow)."""
    spec = importlib_util.find_spec("litellm")
    if spec is None or not spec.origin:
        return {}
    path = Path(spec.origin).resolve().parent / "model_prices_and_context_window_backup.json"
    try:
        with path.open(encoding="utf-8") as handle:
            data = json.load(handle)
        return data if isinstance(data, dict) else {}
    except Exception:
        logger.debug("Could not load LiteLLM price map from %s", path, exc_info=True)
        return {}


def _price_entry(model: str) -> dict | None:
    prices = _model_price_map()
    if not prices:
        return None

    candidates = [model]
    if model.startswith("openrouter/"):
        bare = model.removeprefix("openrouter/")
        candidates.extend(
            (
                bare,
                bare.removeprefix("google/"),
                f"{bare}-preview",
                f"{bare.removeprefix('google/')}-preview",
            )
        )
    elif "/" in model:
        candidates.append(model.split("/", 1)[1])

    seen: set[str] = set()
    for key in candidates:
        if key in seen:
            continue
        seen.add(key)
        entry = prices.get(key)
        if isinstance(entry, dict) and (
            entry.get("input_cost_per_token") is not None
            or entry.get("output_cost_per_token") is not None
        ):
            return entry
    return None


def _estimate_usd(model: str, input_tokens: int, output_tokens: int) -> float:
    entry = _price_entry(model)
    if entry is None:
        return 0.0
    input_rate = float(entry.get("input_cost_per_token") or 0.0)
    output_rate = float(entry.get("output_cost_per_token") or 0.0)
    return max(0.0, input_tokens * input_rate + output_tokens * output_rate)


class ExtractEstimateService:
    def estimate(
        self,
        text: str,
        *,
        mode: ExtractMode = "policy",
        category_hint: str | None = None,
        source_url: str | None = None,
    ) -> ExtractEstimateResponse:
        settings = get_settings()
        model = settings.resolved_llm_model
        expected_output = (
            _POLICY_EXPECTED_OUTPUT_TOKENS
            if mode == "policy"
            else _DOCUMENT_EXPECTED_OUTPUT_TOKENS
        )

        if settings.use_stub_llm:
            return ExtractEstimateResponse(
                model="stub",
                input_tokens=_approx_tokens(text),
                output_tokens=expected_output,
                estimated_cost_usd=0.0,
            )

        source_language = language_label(detect_lang(text))
        if mode == "policy":
            prompt = build_policy_extraction_prompt(
                text,
                source_url=source_url,
                source_language=source_language,
            )
        else:
            prompt = build_document_draft_extraction_prompt(
                text,
                category_hint=category_hint,
                source_url=source_url,
                source_language=source_language,
            )

        input_tokens = _approx_tokens(prompt)
        return ExtractEstimateResponse(
            model=model,
            input_tokens=input_tokens,
            output_tokens=expected_output,
            estimated_cost_usd=_estimate_usd(model, input_tokens, expected_output),
        )
