from __future__ import annotations

import json
import logging
import re
import urllib.request
from abc import ABC, abstractmethod
from dataclasses import dataclass
from typing import Literal

from app.models.protocol import (
    AnimalCounts,
    StudyDomain,
    EndpointCategory,
    RawExtraction,
    Route,
    Species,
)

from app.prompts.extraction import build_extraction_prompt

logger = logging.getLogger(__name__)

RAW_RESPONSE_LOG_LIMIT = 1200
EXTRACTION_MAX_TOKENS = 4096


@dataclass(frozen=True)
class ExtractionError:
    code: Literal["EXTRACTION_FAILED"] = "EXTRACTION_FAILED"
    message: str = "Could not extract parameters from the provided text."
    reason: str | None = None
    raw_response: str | None = None


def truncate_raw_response(text: str | None, *, limit: int = RAW_RESPONSE_LOG_LIMIT) -> str | None:
    if not text:
        return None
    trimmed = text.strip()
    if len(trimmed) <= limit:
        return trimmed
    return f"{trimmed[:limit]}… [truncated, {len(trimmed)} chars total]"


def format_extraction_error(error: ExtractionError) -> str:
    lines = [error.message]
    if error.reason:
        lines.append(f"reason: {error.reason}")
    excerpt = truncate_raw_response(error.raw_response)
    if excerpt:
        lines.append(f"raw_response:\n{excerpt}")
    return "\n".join(lines)


def log_extraction_error(error: ExtractionError) -> None:
    logger.warning("Extraction failed: %s", format_extraction_error(error))


class LLMAdapter(ABC):
    def call(self, prompt: str, *, max_tokens: int, json_mode: bool = False) -> str | None:
        """Send a single-turn prompt; return raw text or None on failure/stub."""
        return None

    @abstractmethod
    def extract_raw_experiments(self, text: str) -> list[RawExtraction] | ExtractionError:
        pass


def _has_extractable_content(raw: RawExtraction) -> bool:
    return bool(raw.study_type.strip()) or bool(raw.procedure_text)


class StubLLMAdapter(LLMAdapter):
    """Heuristic extractor aligned with docs/parameter_model.md."""

    def extract_raw_experiments(self, text: str) -> list[RawExtraction] | ExtractionError:
        raw = self._extract_single(text)
        if isinstance(raw, ExtractionError):
            return raw
        return [raw]

    def _extract_single(self, text: str) -> RawExtraction | ExtractionError:
        normalized = text.strip()
        if len(normalized) < 20:
            return ExtractionError(message="Protocol text is too short to extract parameters.")

        lowered = normalized.lower()
        study_type = self._extract_study_type(lowered)
        if study_type is None:
            return ExtractionError()

        routes = self._extract_routes(lowered)
        species = self._extract_species(lowered)
        animal_counts = self._extract_animal_counts(lowered)
        regulatory = self._extract_regulatory(lowered)
        study_domain = self._extract_study_domain(lowered)
        procedure_text = self._extract_procedure_text(normalized, study_type)

        raw = RawExtraction(
            study_type=study_type,
            route=routes,
            study_domain=study_domain,
            procedure_text=procedure_text,
            species=species,
            animal_counts=animal_counts,
            regulatory=regulatory,
        )

        if not _has_extractable_content(raw):
            return ExtractionError()

        return raw

    @staticmethod
    def _extract_study_type(text: str) -> str | None:
        if re.search(r"ld50|dose letal|lethal dose|acute tox", text):
            return "acute toxicity LD50 study"
        if re.search(r"genotox|mutagen|micronucle|ames", text):
            return "in vivo genotoxicity battery"
        if re.search(r"skin sensiti|alergeni|llna|patch test", text):
            return "skin sensitisation study"
        if re.search(r"ocular|conjunctiv|eye irrit|draize.*eye", text):
            return "ocular irritation study"
        if re.search(r"skin irrit|dermal irrit", text):
            return "skin irritation study"
        if re.search(r"skin corrosion|corrosão cut", text):
            return "skin corrosion study"
        if re.search(r"phototox|3t3 nru", text):
            return "phototoxicity study"
        if re.search(r"pyrogen|endotoxin|mat\b", text):
            return "pyrogenicity study"
        if re.search(r"skin absorption|penetração dérm", text):
            return "skin absorption study"
        return None

    @staticmethod
    def _extract_routes(text: str) -> list[Route] | None:
        routes: list[Route] = []
        if re.search(r"\bp\.?\s*o\.?\b|oral|gavage|gavagem|intrag[aá]stric", text):
            routes.append("oral")
        if re.search(r"\bi\.?\s*p\.?\b|intraperitoneal", text):
            routes.append("intraperitoneal")
        if re.search(r"\bi\.?\s*v\.?\b|intravenous|endovenos", text):
            routes.append("intravenous")
        if re.search(r"dermal|cut[aâ]ne|t[oó]pic|epicut", text):
            routes.append("dermal")
        if re.search(r"ocular|conjunctiv", text):
            routes.append("ocular")
        if re.search(r"inala|inhalation|aerossol|respirat", text):
            routes.append("inhalation")
        if re.search(r"in vitro|cultura celular|c[eé]lulas", text):
            routes.append("in_vitro")
        return routes or None

    @staticmethod
    def _extract_species(text: str) -> Species | None:
        if re.search(r"wistar|sprague|dawley|\brat(s)?\b|rattus", text):
            return "rat"
        if re.search(r"camundong|mouse|mice|mus musculus|balb/c", text):
            return "mouse"
        if re.search(r"rabbit|coelho|cuniculus", text):
            return "rabbit"
        if re.search(r"guinea pig|cobaia|porcellus", text):
            return "guinea_pig"
        if re.search(r"chicken|galinha|gallus", text):
            return "chicken"
        if re.search(r"zebrafish|peixe-zebra|danio", text):
            return "zebrafish"
        if re.search(r"in vitro|cultura celular", text):
            return "in_vitro"
        return None

    @staticmethod
    def _extract_animal_counts(text: str) -> AnimalCounts | None:
        patterns = (
            (r"(\d+)\s+(?:male\s+)?(?:female\s+)?wistar\s+rat", "total"),
            (r"total of\s+(\d+)\s+(?:male\s+)?rat", "total"),
            (r"(\d+)\s+(?:male\s+)?(?:female\s+)?rat", "total"),
            (r"(\d+)\s+animals?", "total"),
        )
        for pattern, field_name in patterns:
            match = re.search(pattern, text, flags=re.IGNORECASE)
            if match:
                return AnimalCounts(**{field_name: int(match.group(1))})
        return None

    @staticmethod
    def _extract_regulatory(text: str) -> bool | None:
        if re.search(
            r"oecd|ecvam|concea|regulatory|directive|ethical committee|"
            r"food safety agency|86/609",
            text,
        ):
            return True
        if re.search(r"non-regulatory|basic research only", text):
            return False
        return None

    @staticmethod
    def _extract_study_domain(text: str) -> StudyDomain:
        if re.search(r"vaccine|pharma|medicinal|drug safety", text):
            return "pharma"
        if re.search(r"cosmetic|higiene pessoal", text):
            return "cosmetics"
        if re.search(
            r"chemical|agrot[oó]x|industrial|essential oil|plant extract|subst[aâ]ncia",
            text,
        ):
            return "chemical_safety"
        return "general"

    @staticmethod
    def _extract_procedure_text(text: str, study_type: str) -> str | None:
        if "acute toxicity" in study_type.lower() and re.search(
            r"ld50|litchfield|wilcoxon", text, re.I
        ):
            return "Single-dose acute toxicity LD50 Litchfield-Wilcoxon"
        if "acute toxicity" in study_type.lower():
            return "Single-dose acute toxicity"
        match = re.search(
            r"(single-dose[^.]{0,80}|28-day[^.]{0,80}|repeated dose[^.]{0,80})",
            text,
            re.IGNORECASE,
        )
        return match.group(1).strip() if match else None


def _normalize_model(model: str) -> str:
    if "/" not in model:
        return f"anthropic/{model}"
    return model


def _repair_json_text(text: str) -> str:
    trimmed = text.strip()
    if re.match(r'^\{"experiments"\s*:', trimmed):
        return trimmed
    match = re.match(r"^(?:\{)?experiments\"\s*:\s*", trimmed)
    if match:
        return '{"experiments": ' + trimmed[match.end() :]
    if trimmed.startswith('"experiments"'):
        return "{" + trimmed
    return trimmed


def _repair_truncated_json(text: str) -> str:
    """Close unterminated strings and open braces/brackets in truncated LLM output."""
    stack: list[str] = []
    in_string = False
    escape = False

    for char in text:
        if in_string:
            if escape:
                escape = False
            elif char == "\\":
                escape = True
            elif char == '"':
                in_string = False
            continue

        if char == '"':
            in_string = True
        elif char == "{":
            stack.append("}")
        elif char == "[":
            stack.append("]")
        elif char in "}]":
            if stack and stack[-1] == char:
                stack.pop()

    repaired = text
    if in_string:
        repaired += '"'

    repaired = repaired.rstrip()
    while repaired.endswith(","):
        repaired = repaired[:-1].rstrip()

    if repaired.endswith(":"):
        repaired += "null"

    repaired += "".join(reversed(stack))
    return repaired


def _collect_json_candidates(raw: str) -> list[str]:
    text = raw.strip()
    candidates: list[str] = []

    def add(candidate: str) -> None:
        stripped = candidate.strip()
        if stripped and stripped not in candidates:
            candidates.append(stripped)

    add(text)

    if text.startswith("```"):
        unfenced = re.sub(r"^```(?:json)?\s*", "", text)
        unfenced = re.sub(r"\s*```$", "", unfenced).strip()
        add(unfenced)

    for match in re.finditer(r"```(?:json)?\s*(.*?)\s*```", text, re.DOTALL | re.IGNORECASE):
        add(match.group(1))

    for match in re.finditer(r'\{\s*"experiments"\s*:', text):
        add(text[match.start() :])

    return candidates


def _parse_json_payload(raw: str) -> object:
    candidates: list[str] = []
    for source in _collect_json_candidates(raw):
        candidates.append(source)
        brace_repaired = _repair_json_text(source)
        if brace_repaired != source:
            candidates.append(brace_repaired)
        truncated = _repair_truncated_json(source)
        if truncated != source:
            candidates.append(truncated)
        if brace_repaired != source:
            truncated_brace = _repair_truncated_json(brace_repaired)
            if truncated_brace not in candidates:
                candidates.append(truncated_brace)

    last_error: json.JSONDecodeError | None = None
    for candidate in candidates:
        try:
            return json.loads(candidate)
        except json.JSONDecodeError as exc:
            last_error = exc

    if last_error is not None:
        raise last_error
    raise json.JSONDecodeError("No JSON candidates to parse", raw.strip(), 0)


def _coerce_animal_counts(payload: dict) -> AnimalCounts | None:
    counts = payload.get("animal_counts")
    if isinstance(counts, dict):
        return AnimalCounts.model_validate(counts)

    legacy_n_animals = payload.pop("n_animals", None)
    if legacy_n_animals is not None:
        return AnimalCounts(total=legacy_n_animals)
    return None


def _coerce_study_domain(payload: dict) -> None:
    domain = payload.get("study_domain")
    if domain is None or (isinstance(domain, str) and not domain.strip()):
        payload["study_domain"] = "general"


def _is_null_route_marker(value: object) -> bool:
    if value is None:
        return True
    if isinstance(value, str):
        return value.strip().lower() in {"", "null", "none"}
    return False


def _coerce_route(payload: dict) -> None:
    route = payload.get("route")
    if route is None:
        return
    if isinstance(route, str):
        payload["route"] = None if _is_null_route_marker(route) else [route]
        return
    if not isinstance(route, list):
        return

    normalized = [item for item in route if not _is_null_route_marker(item)]
    payload["route"] = normalized or None


_SPECIES_ALIASES = frozenset(
    {
        "bovine",
        "cow",
        "cattle",
        "porcine",
        "pig",
        "swine",
        "canine",
        "dog",
        "feline",
        "cat",
        "ovine",
        "sheep",
        "caprine",
        "goat",
        "equine",
        "horse",
    }
)


def _coerce_species(payload: dict) -> None:
    species = payload.get("species")
    if not isinstance(species, str):
        return
    normalized = species.strip().lower()
    if normalized in _SPECIES_ALIASES:
        payload["species"] = "other"


def _raw_from_experiment_item(item: object) -> RawExtraction | None:
    if not isinstance(item, dict):
        return None

    payload = dict(item)
    payload.pop("endpoint_category", None)
    payload.pop("confidence", None)
    payload.pop("raw_text_excerpt", None)
    _coerce_study_domain(payload)
    _coerce_route(payload)
    _coerce_species(payload)
    payload["animal_counts"] = _coerce_animal_counts(payload)

    study_type = payload.get("study_type")
    if not isinstance(study_type, str) or not study_type.strip():
        legacy_endpoint = item.get("endpoint_category") if isinstance(item, dict) else None
        if isinstance(legacy_endpoint, str) and legacy_endpoint:
            payload["study_type"] = legacy_endpoint.replace("_", " ")
        else:
            return None

    try:
        raw = RawExtraction.model_validate(payload)
    except ValueError:
        return None

    if not _has_extractable_content(raw):
        return None
    return raw


def _raw_experiments_from_payload(
    payload: object,
    *,
    raw_response: str | None = None,
) -> list[RawExtraction] | ExtractionError:
    excerpt = truncate_raw_response(raw_response)

    if not isinstance(payload, dict):
        return ExtractionError(
            message="LLM response is not a JSON object.",
            reason="invalid_payload_type",
            raw_response=excerpt,
        )

    if payload.get("error") and not payload.get("experiments"):
        message = payload.get("error")
        if isinstance(message, str) and message:
            return ExtractionError(
                message=message,
                reason="guard_response",
                raw_response=excerpt,
            )
        return ExtractionError(
            reason="guard_response_empty",
            raw_response=excerpt,
        )

    if "experiments" in payload:
        raw_items = payload.get("experiments")
        if not isinstance(raw_items, list) or not raw_items:
            return ExtractionError(
                message="LLM returned an empty experiments array.",
                reason="empty_experiments_array",
                raw_response=excerpt,
            )
        experiments = [
            parsed
            for item in raw_items
            if (parsed := _raw_from_experiment_item(item)) is not None
        ]
        if not experiments:
            return ExtractionError(
                message=f"AI model call returned an invalid response: {excerpt or ''}".rstrip(),
                reason="no_valid_experiment_items",
                raw_response=excerpt,
            )
        return experiments

    single = _raw_from_experiment_item(payload)
    if single is None:
        return ExtractionError(
            message="Single-object LLM response could not be parsed as an experiment.",
            reason="invalid_single_payload",
            raw_response=excerpt,
        )
    return [single]


def _extract_from_raw(raw: str) -> list[RawExtraction] | ExtractionError:
    try:
        payload = _parse_json_payload(raw)
    except json.JSONDecodeError as exc:
        error = ExtractionError(
            message=f"LLM response is not valid JSON: {exc}",
            reason="json_decode_error",
            raw_response=truncate_raw_response(raw),
        )
        log_extraction_error(error)
        return error
    parsed = _raw_experiments_from_payload(payload, raw_response=raw)
    if isinstance(parsed, ExtractionError):
        log_extraction_error(parsed)
    return parsed


class LlmCallAdapter(LLMAdapter):
    def __init__(self, model: str) -> None:
        self._model = _normalize_model(model)

    def call(self, prompt: str, *, max_tokens: int, json_mode: bool = False) -> str | None:
        try:
            import llmcall as _llmcall
            from llmcall import CallConstraints, LLMError as LlmCallError
        except ImportError:
            logger.warning("llmcall package is not installed")
            return None
        kwargs: dict = {"max_tokens": max_tokens}
        if json_mode:
            kwargs["response_format"] = "json"
        result = _llmcall.call(self._model, prompt, constraints=CallConstraints(**kwargs))
        if isinstance(result, LlmCallError):
            logger.warning("LLM API error: %s", result.message)
            return None
        return result.content

    def extract_raw_experiments(self, text: str) -> list[RawExtraction] | ExtractionError:
        raw = self.call(build_extraction_prompt(text), max_tokens=EXTRACTION_MAX_TOKENS, json_mode=True)
        if raw is None:
            return ExtractionError(message="LLM call returned no response.")
        return _extract_from_raw(raw)


class OllamaLLMAdapter(LLMAdapter):
    """Calls a locally-running Ollama server (default: http://localhost:11434)."""

    def __init__(self, model: str, base_url: str = "http://localhost:11434") -> None:
        self._model = model
        self._base_url = base_url.rstrip("/")

    def call(self, prompt: str, *, max_tokens: int, json_mode: bool = False) -> str | None:
        payload: dict = {
            "model": self._model,
            "prompt": prompt,
            "stream": False,
            "options": {"num_predict": max_tokens},
        }
        if json_mode:
            payload["format"] = "json"
        data = json.dumps(payload).encode()
        req = urllib.request.Request(
            f"{self._base_url}/api/generate",
            data=data,
            headers={"Content-Type": "application/json"},
            method="POST",
        )
        try:
            with urllib.request.urlopen(req, timeout=60) as resp:
                body = json.loads(resp.read())
            return body.get("response")
        except Exception as exc:
            logger.warning("Ollama call failed: %s", exc)
            return None

    def extract_raw_experiments(self, text: str) -> list[RawExtraction] | ExtractionError:
        raw = self.call(build_extraction_prompt(text), max_tokens=EXTRACTION_MAX_TOKENS, json_mode=True)
        if raw is None:
            return ExtractionError(message="Ollama call returned no response.")
        return _extract_from_raw(raw)


def build_llm_adapter(
    *,
    model: str,
    use_stub: bool,
    ollama_model: str | None = None,
) -> LLMAdapter:
    if ollama_model:
        return OllamaLLMAdapter(model=ollama_model)
    if use_stub:
        return StubLLMAdapter()
    return LlmCallAdapter(model=model)
