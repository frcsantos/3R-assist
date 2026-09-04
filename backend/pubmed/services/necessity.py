from __future__ import annotations

import json
import logging

from app.adapters.llm import LLMAdapter
from app.models.protocol import ProtocolParameters

from pubmed.models.analysis import NecessityAssessment
from pubmed.prompts.necessity import build_necessity_prompt

logger = logging.getLogger(__name__)

_MAX_TOKENS = 1024
_VALID_VERDICTS = {"necessary", "possibly_avoidable", "not_necessary"}
_VALID_CONFIDENCE = {"high", "medium", "low"}


def _fallback(reason: str) -> NecessityAssessment:
    logger.warning("Necessity assessment failed: %s", reason)
    return NecessityAssessment(
        verdict="necessary",
        confidence="low",
        rationale="Assessment could not be completed. Defaulting to 'necessary' as a precaution.",
        key_concerns=["Automated assessment unavailable — manual review required"],
        suggested_approach=None,
    )


class NecessityService:
    def __init__(self, llm: LLMAdapter) -> None:
        self._llm = llm

    def assess(
        self,
        protocol_text: str,
        params: ProtocolParameters,
    ) -> NecessityAssessment:
        prompt = build_necessity_prompt(
            protocol_text=protocol_text,
            endpoint_category=params.endpoint_category,
            study_domain=params.study_domain,
            species=params.species,
            route=params.route,
            procedure_text=params.procedure_text,
            regulatory=params.regulatory,
        )

        raw = self._llm.call(prompt, max_tokens=_MAX_TOKENS, json_mode=True)
        if raw is None:
            return _fallback("LLM unavailable — no model configured or call failed")

        try:
            payload = json.loads(raw)
        except json.JSONDecodeError as exc:
            return _fallback(f"JSON parse error: {exc}")

        verdict = payload.get("verdict", "necessary")
        if verdict not in _VALID_VERDICTS:
            verdict = "necessary"

        confidence = payload.get("confidence", "low")
        if confidence not in _VALID_CONFIDENCE:
            confidence = "low"

        return NecessityAssessment(
            verdict=verdict,
            confidence=confidence,
            rationale=payload.get("rationale", ""),
            key_concerns=payload.get("key_concerns", []),
            suggested_approach=payload.get("suggested_approach"),
        )
