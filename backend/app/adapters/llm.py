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
    Application,
    EndpointCategory,
    RawExtraction,
    Route,
    Species,
    coerce_application,
    coerce_route_list,
)
from app.models.method import AnimalUse, RegulatoryStatus, TestSystem
from app.models.method_draft import MethodDraftExtractResponse, MethodDraftFields
from app.models.document_draft import DocumentDraftExtractResponse, DocumentDraftFields
from app.models.regulation_draft import (
    RegulationDraftExtractResponse,
    RegulationDraftFields,
)
from app.models.i18n import localized_str, localized_str_list, parse_localized_str
from app.models.jurisdiction import jurisdiction_for_code, parse_jurisdiction
from app.models.policy import PolicyExtractResponse, PolicyMethod
from app.prompts.document_draft_extraction import build_document_draft_extraction_prompt
from app.prompts.extraction import build_extraction_prompt
from app.prompts.method_draft_extraction import build_method_draft_extraction_prompt
from app.prompts.policy_extraction import build_policy_extraction_prompt
from app.prompts.regulation_draft_extraction import (
    build_regulation_draft_extraction_prompt,
)
from app.services.oecd_citation import prefer_oecd_tg_citation

logger = logging.getLogger(__name__)

RAW_RESPONSE_LOG_LIMIT = 1200
EXTRACTION_MAX_TOKENS = 4096
POLICY_EXTRACTION_MAX_TOKENS = 4096
METHOD_DRAFT_EXTRACTION_MAX_TOKENS = 4096
DOCUMENT_DRAFT_EXTRACTION_MAX_TOKENS = 2048
REGULATION_DRAFT_EXTRACTION_MAX_TOKENS = 2048

_DOCUMENT_CATEGORY_VALUES: frozenset[str] = frozenset(
    {"method_protocol", "guideline", "regulation", "other"}
)
_DESCRIPTION_MAX_CHARS = 300

_REGULATORY_STATUS_VALUES: frozenset[str] = frozenset(
    {"not_approved", "approved", "recommended", "mandatory"}
)
_ENDPOINT_CATEGORY_VALUES: frozenset[str] = frozenset(
    {
        "acute_toxicity",
        "skin_irritation",
        "skin_corrosion",
        "ocular_irritation",
        "skin_sensitisation",
        "phototoxicity",
        "genotoxicity",
        "pyrogenicity",
        "skin_absorption",
        "reproductive_toxicity",
        "endocrine_activity",
        "photoreactivity",
        "aquatic_toxicity",
        "toxicokinetics",
        "bacterial_endotoxin",
        "rabies_diagnosis",
    }
)
_APPLICATION_VALUES: frozenset[str] = frozenset(
    {
        "basic-research",
        "translational-applied-research",
        "regulatory-use",
        "routine-production",
        "education-training",
        "environmental-protection",
        "species-preservation",
        "forensic-inquiry",
        "other",
    }
)
_ANIMAL_USE_VALUES: frozenset[str] = frozenset(
    {
        "none",
        "animal_derived_material",
        "slaughterhouse_byproduct",
        "animals_killed_for_tissue",
        "live_animals",
        "mixed_or_variable",
    }
)
_TEST_SYSTEM_VALUES: frozenset[str] = frozenset(
    {
        "in_silico",
        "in_chemico",
        "in_vitro",
        "ex_vivo",
        "in_vivo",
        "hybrid",
        "unclear",
    }
)
_SOURCE_DB_VALUES: frozenset[str] = frozenset(
    {"OECD_TG", "ECVAM_DBALM", "NICEATM", "FARMACOPEIA_BR", "TSAR"}
)

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

    async def async_call(self, prompt: str, *, max_tokens: int, json_mode: bool = False) -> str | None:
        """Non-blocking wrapper around call() for use in async contexts."""
        import asyncio
        return await asyncio.get_event_loop().run_in_executor(
            None, lambda: self.call(prompt, max_tokens=max_tokens, json_mode=json_mode)
        )

    @abstractmethod
    def extract_raw_experiments(
        self,
        text: str,
        *,
        source_language: str = "English",
    ) -> list[RawExtraction] | ExtractionError:
        pass

    @abstractmethod
    def extract_policy(
        self,
        text: str,
        *,
        source_url: str | None = None,
        source_language: str = "English",
    ) -> PolicyExtractResponse | ExtractionError:
        pass

    @abstractmethod
    def extract_method_draft(
        self, text: str
    ) -> MethodDraftExtractResponse | ExtractionError:
        pass

    @abstractmethod
    def extract_document_draft(
        self,
        text: str,
        *,
        category_hint: str | None = None,
        source_url: str | None = None,
        source_language: str = "English",
    ) -> DocumentDraftExtractResponse | ExtractionError:
        pass

    @abstractmethod
    def extract_regulation_draft(
        self,
        text: str,
        *,
        source_url: str | None = None,
    ) -> RegulationDraftExtractResponse | ExtractionError:
        pass


def _has_extractable_content(raw: RawExtraction) -> bool:
    return bool(raw.study_type.strip()) or bool(raw.procedure_text)


class StubLLMAdapter(LLMAdapter):
    """Heuristic extractor aligned with docs/parameter_model.md."""

    def extract_raw_experiments(
        self,
        text: str,
        *,
        source_language: str = "English",
    ) -> list[RawExtraction] | ExtractionError:
        raw = self._extract_single(text)
        if isinstance(raw, ExtractionError):
            return raw
        return [raw]

    def extract_policy(
        self,
        text: str,
        *,
        source_url: str | None = None,
        source_language: str = "English",
    ) -> PolicyExtractResponse | ExtractionError:
        normalized = text.strip()
        if len(normalized) < 20:
            return ExtractionError(
                message="Text is too short to extract policy methods.",
                reason="text_too_short",
            )

        methods: list[PolicyMethod] = []
        for match in re.finditer(
            r"(?:OECD\s+)?TG\s*(\d{3,4})\b(?:\s*[:\-–—]\s*([^\n.;]{3,120}))?",
            normalized,
            flags=re.IGNORECASE,
        ):
            code = f"TG {match.group(1)}"
            name = (match.group(2) or "").strip() or f"OECD Test Guideline {match.group(1)}"
            if not any(item.code == code for item in methods):
                methods.append(PolicyMethod(code=code, name=name, purpose=None))

        document_name = None
        title_match = re.search(
            r"(?im)^(?:title|documento|document|citation|resolu[cç][aã]o|guideline)\s*[:\-–—]\s*(.+)$",
            normalized,
        )
        if title_match:
            document_name = title_match.group(1).strip()[:240]

        document_date = None
        date_match = re.search(
            r"\b(20\d{2}-\d{2}-\d{2}|\d{1,2}[./]\d{1,2}[./]20\d{2}|20\d{2})\b",
            normalized,
        )
        if date_match:
            document_date = date_match.group(1)

        institution = None
        for candidate in (
            "CONCEA",
            "OECD",
            "ICH",
            "ISO",
            "EMA",
            "FDA",
            "ANVISA",
            "NC3Rs",
            "ECHA",
        ):
            if re.search(rf"\b{re.escape(candidate)}\b", normalized, flags=re.IGNORECASE):
                institution = candidate
                break

        url = _nullable_str(source_url)
        url_match = re.search(r"https?://[^\s<>\"']+", normalized, flags=re.IGNORECASE)
        if url_match:
            url = url_match.group(0).rstrip(".,);]")

        description = None
        purpose_match = re.search(
            r"(?is)\b(?:description|descri(?:ption|ção)|summary|resumo|scope|objetivo)\s*[:\-–—]\s*(.+?)(?:\n\n|$)",
            normalized,
        )
        if purpose_match:
            description = " ".join(purpose_match.group(1).split())[:_DESCRIPTION_MAX_CHARS]

        document_name = prefer_oecd_tg_citation(document_name, normalized)

        return PolicyExtractResponse(
            methods=methods,
            document_name=document_name,
            document_date=document_date,
            responsible_institution=institution,
            url=url,
            description=description,
        )

    def extract_method_draft(
        self, text: str
    ) -> MethodDraftExtractResponse | ExtractionError:
        normalized = text.strip()
        if len(normalized) < 20:
            return ExtractionError(
                message="Text is too short to extract method fields.",
                reason="text_too_short",
            )

        tg_match = re.search(
            r"(?:OECD\s+)?TG\s*(\d{3,4})\b(?:\s*[:\-–—]\s*([^\n.;]{3,120}))?",
            normalized,
            flags=re.IGNORECASE,
        )
        oecd_ref = f"TG {tg_match.group(1)}" if tg_match else None
        title = (tg_match.group(2) if tg_match else None) or None
        if not title:
            title_match = re.search(
                r"(?im)^(?:title|name|method|guideline)\s*[:\-–—]\s*(.+)$",
                normalized,
            )
            title = title_match.group(1).strip()[:240] if title_match else None
        if not title and oecd_ref:
            title = f"OECD Test Guideline {oecd_ref.removeprefix('TG ').strip()}"
        if not title:
            title = normalized.split("\n", 1)[0].strip()[:120] or "Untitled method"

        description = None
        purpose_match = re.search(
            r"(?is)\b(?:purpose|objective|scope|descri(?:ption|ção))\s*[:\-–—]\s*(.+?)(?:\n\n|$)",
            normalized,
        )
        if purpose_match:
            description = " ".join(purpose_match.group(1).split())[:800]

        endpoint = self._method_endpoint(normalized.lower())
        routes = self._extract_routes(normalized.lower())
        study_domain = self._extract_application(normalized.lower())
        animal_use = self._extract_animal_use(normalized.lower())
        test_system = self._extract_test_system(normalized.lower())
        slug_seed = (
            f"oecd-tg{tg_match.group(1)}-{title}" if tg_match else title
        )
        slug = _slugify_method(slug_seed)
        if oecd_ref and not slug.startswith("oecd-"):
            slug = f"oecd-{slug}"

        fields = MethodDraftFields(
            slug=slug[:80],
            name=localized_str(title),
            description=localized_str(description or title),
            animal_use=animal_use,
            test_system=test_system,
            endpoint_category=endpoint,
            routes_applicable=routes,
            application=study_domain,
            oecd_ref=oecd_ref,
            source_db="OECD_TG" if oecd_ref else None,
            text_for_embedding=" — ".join(
                part for part in (oecd_ref, title, description) if part
            ),
            active=False,
        )
        return MethodDraftExtractResponse(fields=fields)

    def extract_document_draft(
        self,
        text: str,
        *,
        category_hint: str | None = None,
        source_url: str | None = None,
        source_language: str = "English",
    ) -> DocumentDraftExtractResponse | ExtractionError:
        normalized = text.strip()
        if len(normalized) < 20:
            return ExtractionError(
                message="Text is too short to extract document fields.",
                reason="text_too_short",
            )

        title = None
        title_match = re.search(
            r"(?im)^(?:title|documento|document|citation|guideline|protocol)\s*[:\-–—]\s*(.+)$",
            normalized,
        )
        if title_match:
            title = title_match.group(1).strip()[:240]
        if not title:
            title = normalized.split("\n", 1)[0].strip()[:160] or "Untitled document"

        document_date = None
        date_match = re.search(
            r"\b(20\d{2}-\d{2}-\d{2}|\d{1,2}[./]\d{1,2}[./]20\d{2}|20\d{2})\b",
            normalized,
        )
        if date_match:
            raw_date = date_match.group(1)
            if re.fullmatch(r"20\d{2}", raw_date):
                document_date = f"{raw_date}-01-01"
            else:
                document_date = raw_date

        url = source_url
        url_match = re.search(r"https?://[^\s<>\"']+", normalized, flags=re.IGNORECASE)
        if url_match:
            url = url_match.group(0).rstrip(".,);]")

        category = category_hint if category_hint in _DOCUMENT_CATEGORY_VALUES else None
        if category is None:
            lower = normalized.lower()
            if re.search(r"\b(regulament|regulation|decree|resolu)", lower):
                category = "regulation"
            elif re.search(r"\b(guideline|guidance|diretriz)\b", lower):
                category = "guideline"
            elif re.search(r"\b(protocol|test guideline|\btg\s*\d)", lower):
                category = "method_protocol"
            else:
                category = "other"

        description_raw = " ".join(normalized.split())[:_DESCRIPTION_MAX_CHARS]
        citation_text = prefer_oecd_tg_citation(title, normalized) or title

        return DocumentDraftExtractResponse(
            fields=DocumentDraftFields(
                slug=_slugify_method(citation_text)[:80] or None,
                date=document_date,
                url=url,
                categories=[category],  # type: ignore[list-item]
                doc_citation=localized_str(citation_text),
                description=localized_str(description_raw),
            )
        )

    def extract_regulation_draft(
        self,
        text: str,
        *,
        source_url: str | None = None,
    ) -> RegulationDraftExtractResponse | ExtractionError:
        _ = source_url
        normalized = text.strip()
        if len(normalized) < 20:
            return ExtractionError(
                message="Text is too short to extract regulation fields.",
                reason="text_too_short",
            )
        lowered = normalized.lower()

        jurisdiction = None
        if re.search(r"\bbrazil\b|\bbrasil\b|concea|anvisa", lowered):
            jurisdiction = jurisdiction_for_code("brazil")
        elif re.search(r"\boecd\b", lowered):
            jurisdiction = jurisdiction_for_code("oecd")
        elif re.search(r"\beu\b|european union|echa|ema\b", lowered):
            jurisdiction = jurisdiction_for_code("eu")
        elif re.search(r"\bus\b|united states|\bfda\b|\bepa\b|iccvam", lowered):
            jurisdiction = jurisdiction_for_code("us")

        regulatory_status = None
        if re.search(r"\bmandatory\b|obrigat", lowered):
            regulatory_status = "mandatory"
        elif re.search(r"\brecommended\b|recomend", lowered):
            regulatory_status = "recommended"
        elif re.search(r"\bapproved\b|aprovad", lowered):
            regulatory_status = "approved"
        elif re.search(r"not approved|não aprov|nao aprov", lowered):
            regulatory_status = "not_approved"

        regulatory_date = None
        date_match = re.search(
            r"\b(20\d{2}-\d{2}-\d{2}|\d{1,2}[./]\d{1,2}[./]20\d{2}|20\d{2})\b",
            normalized,
        )
        if date_match:
            raw_date = date_match.group(1)
            regulatory_date = (
                f"{raw_date}-01-01"
                if re.fullmatch(r"20\d{2}", raw_date)
                else raw_date
            )

        body = None
        for candidate in (
            "CONCEA",
            "ANVISA",
            "ECHA",
            "EMA",
            "EPA",
            "FDA",
            "ICCVAM",
            "OECD",
        ):
            if re.search(rf"\b{re.escape(candidate)}\b", normalized, re.I):
                body = candidate
                break

        return RegulationDraftExtractResponse(
            fields=RegulationDraftFields(
                jurisdiction=jurisdiction,
                regulatory_status=regulatory_status,  # type: ignore[arg-type]
                regulatory_date=regulatory_date,
                regulatory_endpoints=None,
                endpoint_quote=None,
                regulatory_body=localized_str(body) if body else None,
                regulatory_citation=None,
                notes=None,
            )
        )

    @staticmethod
    def _method_endpoint(text: str) -> EndpointCategory | None:
        if re.search(r"skin sensiti|llna|alergeni", text):
            return "skin_sensitisation"
        if re.search(r"skin corrosion|corros", text):
            return "skin_corrosion"
        if re.search(r"skin irrit|dermal irrit|epiderm", text):
            return "skin_irritation"
        if re.search(r"ocular|eye irrit|bcop|draize.*eye", text):
            return "ocular_irritation"
        if re.search(r"phototox", text):
            return "phototoxicity"
        if re.search(r"genotox|ames|micronucle|mutagen", text):
            return "genotoxicity"
        if re.search(r"pyrogen|mat\b|monocyte activation", text):
            return "pyrogenicity"
        if re.search(r"bacterial endotoxin|lal test|bet assay", text):
            return "bacterial_endotoxin"
        if re.search(r"absorption|permeab|dermal penetr", text):
            return "skin_absorption"
        if re.search(
            r"reproductive|developmental tox|teratogen|fertility|embryo.?fetal",
            text,
        ):
            return "reproductive_toxicity"
        if re.search(r"endocrine|estrogenic|androgenic|steroidogenic", text):
            return "endocrine_activity"
        if re.search(r"photoreactiv", text):
            return "photoreactivity"
        if re.search(r"aquatic tox|fish embryo|daphnia", text):
            return "aquatic_toxicity"
        if re.search(r"toxicokinetic|adme|intrinsic clearance", text):
            return "toxicokinetics"
        if re.search(r"rabies", text):
            return "rabies_diagnosis"
        if re.search(r"acute tox|ld50|fixed dose|atc\b|udp\b", text):
            return "acute_toxicity"
        return None

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
        study_domain = self._extract_application(lowered)
        procedure_text = self._extract_procedure_text(normalized, study_type)

        raw = RawExtraction(
            study_type=study_type,
            route=routes,
            application=study_domain,
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
            routes.append("cutaneous")
        if re.search(r"ocular|conjunctiv", text):
            routes.append("ocular")
        if re.search(r"inala|inhalation|aerossol|respirat", text):
            routes.append("inhalation")
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
    def _extract_application(text: str) -> Application:
        if re.search(r"educat|training|ensino|treinamento", text):
            return "education-training"
        if re.search(r"forensic|criminalist|judicial", text):
            return "forensic-inquiry"
        if re.search(r"conservat|species preservation|endangered", text):
            return "species-preservation"
        if re.search(r"environment|ecolog|meio ambiente", text):
            return "environmental-protection"
        if re.search(r"batch release|potency testing|quality control|manufactur", text):
            return "routine-production"
        if re.search(r"oecd|regulatory|guideline|reach|anvisa|fda", text):
            return "regulatory-use"
        if re.search(r"vaccine|pharma|medicinal|drug safety|diagnos|treatment", text):
            return "translational-applied-research"
        if re.search(r"cosmetic|higiene pessoal", text):
            return "regulatory-use"
        if re.search(
            r"chemical|agrot[oó]x|industrial|essential oil|plant extract|subst[aâ]ncia",
            text,
        ):
            return "regulatory-use"
        return "basic-research"

    @staticmethod
    def _extract_animal_use(text: str) -> AnimalUse | None:
        hits: list[AnimalUse] = []
        if re.search(
            r"live animal|in vivo animal|conscious animal|anesthetized animal|"
            r"animal experiment|labou?ratory animal",
            text,
        ):
            hits.append("live_animals")
        if re.search(
            r"slaughterhouse|abattoir|food.?chain animal|already slaughtered",
            text,
        ):
            hits.append("slaughterhouse_byproduct")
        if re.search(
            r"killed for (?:tissue|organ)|sacrificed for (?:tissue|organ)|"
            r"animals? (?:were )?killed to obtain",
            text,
        ):
            hits.append("animals_killed_for_tissue")
        if re.search(
            r"fetal bovine serum|fbs\b|animal.?derived|serum|antibody from|"
            r"animal product",
            text,
        ):
            hits.append("animal_derived_material")
        if re.search(
            r"\bno animals?\b|animal.?free|non.?animal|without animals",
            text,
        ):
            hits.append("none")
        unique = list(dict.fromkeys(hits))
        if not unique:
            return None
        if len(unique) > 1:
            return "mixed_or_variable"
        return unique[0]

    @staticmethod
    def _extract_test_system(text: str) -> list[TestSystem] | None:
        systems: list[TestSystem] = []
        if re.search(r"in silico|computational|qsar|read.?across model", text):
            systems.append("in_silico")
        if re.search(r"in chemico|dpra|peptide reactivity|chemical reactivity assay", text):
            systems.append("in_chemico")
        if re.search(r"in vitro|cell culture|reconstructed|organoid|3d model", text):
            systems.append("in_vitro")
        if re.search(r"ex vivo|excised|isolated organ|corneal opacity", text):
            systems.append("ex_vivo")
        if re.search(r"\bin vivo\b|whole animal", text):
            systems.append("in_vivo")
        if re.search(r"\bhybrid\b|integrated approach|iata\b|defined approach", text):
            systems.append("hybrid")
        return systems or None

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


_VALID_STUDY_DOMAINS = frozenset({"pharma", "cosmetics", "chemical_safety", "general"})
_VALID_SPECIES = frozenset(
    {"rat", "mouse", "rabbit", "guinea_pig", "chicken", "zebrafish", "in_vitro", "other"}
)
_VALID_ROUTES = frozenset(
    {"oral", "intraperitoneal", "intravenous", "dermal", "ocular", "inhalation", "in_vitro", "other"}
)
_SPECIES_ALIASES: dict[str, str] = {
    "bovine": "other", "cow": "other", "cattle": "other",
    "porcine": "other", "pig": "other", "swine": "other",
    "canine": "other", "dog": "other",
    "feline": "other", "cat": "other",
    "ovine": "other", "sheep": "other",
    "caprine": "other", "goat": "other",
    "equine": "other", "horse": "other",
    "wistar": "rat", "sprague": "rat", "sprague-dawley": "rat",
    "rattus": "rat", "rattus norvegicus": "rat",
    "mus musculus": "mouse", "balb/c": "mouse", "c57bl/6": "mouse",
    "oryctolagus": "rabbit", "new zealand white": "rabbit",
    "danio rerio": "zebrafish",
    "cavia porcellus": "guinea_pig",
    "gallus gallus": "chicken",
}
_ROUTE_ALIASES: dict[str, str] = {
    "gavage": "oral", "intragastric": "oral", "p.o.": "oral", "per os": "oral",
    "dietary": "oral", "intragástrico": "oral",
    "i.p.": "intraperitoneal", "ip": "intraperitoneal",
    "i.v.": "intravenous", "iv": "intravenous", "endovenous": "intravenous",
    "topical": "dermal", "cutaneous": "dermal", "epicutaneous": "dermal",
    "instillation": "ocular", "conjunctival": "ocular",
    "aerosol": "inhalation", "inhalation chamber": "inhalation",
}


def _coerce_study_domain(payload: dict) -> None:
    domain = payload.get("study_domain")
    if not isinstance(domain, str) or domain.strip().lower() not in _VALID_STUDY_DOMAINS:
        payload["study_domain"] = "general"


def _coerce_application(payload: dict) -> None:
    raw = payload.get("application")
    if raw is None or (isinstance(raw, str) and not raw.strip()):
        raw = payload.get("study_domain")
    payload["application"] = coerce_application(raw)
    if payload.get("application_evidence") is None:
        payload["application_evidence"] = payload.get("study_domain_evidence")
    if payload.get("application_confidence") is None:
        payload["application_confidence"] = payload.get("study_domain_confidence")


def _is_null_route_marker(value: object) -> bool:
    if value is None:
        return True
    if isinstance(value, str):
        return value.strip().lower() in {"", "null", "none"}
    return False


def _normalize_route_value(value: str) -> str | None:
    v = value.strip().lower()
    if v in _VALID_ROUTES:
        return v
    if v in _ROUTE_ALIASES:
        return _ROUTE_ALIASES[v]
    return "other"


def _coerce_route(payload: dict) -> None:
    route = payload.get("route")
    if route is None:
        return
    if isinstance(route, str):
        if _is_null_route_marker(route):
            payload["route"] = None
        else:
            normalized = _normalize_route_value(route)
            payload["route"] = [normalized] if normalized else None
        return
    if not isinstance(route, list):
        payload["route"] = None
        return

    valid = []
    for item in route:
        if _is_null_route_marker(item):
            continue
        if isinstance(item, str):
            normalized = _normalize_route_value(item)
            if normalized:
                valid.append(normalized)
    payload["route"] = valid or None


def _coerce_species(payload: dict) -> None:
    species = payload.get("species")
    if not isinstance(species, str):
        return
    normalized = species.strip().lower()
    if normalized in _VALID_SPECIES:
        return
    if normalized in _SPECIES_ALIASES:
        payload["species"] = _SPECIES_ALIASES[normalized]
    else:
        # Unknown species string — drop rather than fail validation
        payload["species"] = None


def _raw_from_experiment_item(item: object) -> RawExtraction | None:
    if not isinstance(item, dict):
        return None

    payload = dict(item)
    payload.pop("endpoint_category", None)
    payload.pop("confidence", None)
    payload.pop("raw_text_excerpt", None)
    _coerce_application(payload)
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
        kwargs: dict = {"max_tokens": max_tokens, "temperature": 0.0}
        if json_mode:
            kwargs["response_format"] = "json"
        result = _llmcall.call(self._model, prompt, constraints=CallConstraints(**kwargs))
        if isinstance(result, LlmCallError):
            logger.warning("LLM API error: %s", result.message)
            return None
        return result.content
      
    def extract_raw_experiments(
        self,
        text: str,
        *,
        source_language: str = "English",
    ) -> list[RawExtraction] | ExtractionError:
        try:
            import llmcall as _llmcall
            from llmcall import CallConstraints, LLMError as LlmCallError
        except ImportError:
            return ExtractionError(message="llmcall package is not installed.")

        result = llmcall.call(
            self._model,
            build_extraction_prompt(text, source_language=source_language),
            constraints=CallConstraints(
                max_tokens=EXTRACTION_MAX_TOKENS,
                response_format="json",
            ),
        )
        if isinstance(result, LlmCallError):
            logger.warning("LLM API error: %s", result.message)
            return None
        return result.content


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
            "keep_alive": -1,
            "options": {"num_predict": max_tokens, "temperature": 0.0, "num_ctx": 16384, "seed": 42},
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
            with urllib.request.urlopen(req, timeout=180) as resp:
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

    def extract_policy(
        self,
        text: str,
        *,
        source_url: str | None = None,
        source_language: str = "English",
    ) -> PolicyExtractResponse | ExtractionError:
        try:
            import llmcall
            from llmcall import CallConstraints, LLMError as LlmCallError
        except ImportError:
            return ExtractionError(message="llmcall package is not installed.")

        result = llmcall.call(
            self._model,
            build_policy_extraction_prompt(
                text,
                source_url=source_url,
                source_language=source_language,
            ),
            constraints=CallConstraints(
                max_tokens=POLICY_EXTRACTION_MAX_TOKENS,
                response_format="json",
            ),
        )
        if isinstance(result, LlmCallError):
            error = ExtractionError(
                message=result.message,
                reason="llm_api_error",
            )
            log_extraction_error(error)
            return error

        raw_content = result.content
        try:
            payload = _parse_json_payload(raw_content)
        except json.JSONDecodeError as exc:
            error = ExtractionError(
                message=f"LLM response is not valid JSON: {exc}",
                reason="json_decode_error",
                raw_response=truncate_raw_response(raw_content),
            )
            log_extraction_error(error)
            return error

        parsed = _policy_from_payload(
            payload,
            raw_response=raw_content,
            source_url=source_url,
            source_text=text,
        )
        if isinstance(parsed, ExtractionError):
            log_extraction_error(parsed)
        return parsed

    def extract_method_draft(
        self, text: str
    ) -> MethodDraftExtractResponse | ExtractionError:
        try:
            import llmcall
            from llmcall import CallConstraints, LLMError as LlmCallError
        except ImportError:
            return ExtractionError(message="llmcall package is not installed.")

        result = llmcall.call(
            self._model,
            build_method_draft_extraction_prompt(text),
            constraints=CallConstraints(
                max_tokens=METHOD_DRAFT_EXTRACTION_MAX_TOKENS,
                response_format="json",
            ),
        )
        if isinstance(result, LlmCallError):
            error = ExtractionError(
                message=result.message,
                reason="llm_api_error",
            )
            log_extraction_error(error)
            return error

        raw_content = result.content
        try:
            payload = _parse_json_payload(raw_content)
        except json.JSONDecodeError as exc:
            error = ExtractionError(
                message=f"LLM response is not valid JSON: {exc}",
                reason="json_decode_error",
                raw_response=truncate_raw_response(raw_content),
            )
            log_extraction_error(error)
            return error

        parsed = _method_draft_from_payload(
            payload,
            raw_response=raw_content,
        )
        if isinstance(parsed, ExtractionError):
            log_extraction_error(parsed)
        return parsed

    def extract_document_draft(
        self,
        text: str,
        *,
        category_hint: str | None = None,
        source_url: str | None = None,
        source_language: str = "English",
    ) -> DocumentDraftExtractResponse | ExtractionError:
        try:
            import llmcall
            from llmcall import CallConstraints, LLMError as LlmCallError
        except ImportError:
            return ExtractionError(message="llmcall package is not installed.")

        result = llmcall.call(
            self._model,
            build_document_draft_extraction_prompt(
                text,
                category_hint=category_hint,
                source_url=source_url,
                source_language=source_language,
            ),
            constraints=CallConstraints(
                max_tokens=DOCUMENT_DRAFT_EXTRACTION_MAX_TOKENS,
                response_format="json",
            ),
        )
        if isinstance(result, LlmCallError):
            error = ExtractionError(
                message=result.message,
                reason="llm_api_error",
            )
            log_extraction_error(error)
            return error

        raw_content = result.content
        try:
            payload = _parse_json_payload(raw_content)
        except json.JSONDecodeError as exc:
            error = ExtractionError(
                message=f"LLM response is not valid JSON: {exc}",
                reason="json_decode_error",
                raw_response=truncate_raw_response(raw_content),
            )
            log_extraction_error(error)
            return error

        parsed = _document_draft_from_payload(
            payload,
            category_hint=category_hint,
            source_url=source_url,
            source_text=text,
            raw_response=raw_content,
        )
        if isinstance(parsed, ExtractionError):
            log_extraction_error(parsed)
        return parsed

    def extract_regulation_draft(
        self,
        text: str,
        *,
        source_url: str | None = None,
    ) -> RegulationDraftExtractResponse | ExtractionError:
        try:
            import llmcall
            from llmcall import CallConstraints, LLMError as LlmCallError
        except ImportError:
            return ExtractionError(message="llmcall package is not installed.")

        result = llmcall.call(
            self._model,
            build_regulation_draft_extraction_prompt(text, source_url=source_url),
            constraints=CallConstraints(
                max_tokens=REGULATION_DRAFT_EXTRACTION_MAX_TOKENS,
                response_format="json",
            ),
        )
        if isinstance(result, LlmCallError):
            error = ExtractionError(
                message=result.message,
                reason="llm_api_error",
            )
            log_extraction_error(error)
            return error

        raw_content = result.content
        try:
            payload = _parse_json_payload(raw_content)
        except json.JSONDecodeError as exc:
            error = ExtractionError(
                message=f"LLM response is not valid JSON: {exc}",
                reason="json_decode_error",
                raw_response=truncate_raw_response(raw_content),
            )
            log_extraction_error(error)
            return error

        parsed = _regulation_draft_from_payload(
            payload,
            raw_response=raw_content,
        )
        if isinstance(parsed, ExtractionError):
            log_extraction_error(parsed)
        return parsed


def _nullable_str(value: object) -> str | None:
    if value is None:
        return None
    text = str(value).strip()
    if not text or text.lower() in {"null", "none", "n/a", "na"}:
        return None
    return text


def _nullable_regulatory_status(value: object) -> RegulatoryStatus | None:
    text = _nullable_str(value)
    if text is None:
        return None
    normalized = text.lower().replace(" ", "_").replace("-", "_")
    if normalized in _REGULATORY_STATUS_VALUES:
        return normalized  # type: ignore[return-value]
    return None


def _int_list_from_payload(value: object) -> list[int] | None:
    if value is None:
        return None
    if isinstance(value, str):
        text = value.strip()
        if not text or text.lower() in {"null", "none", "n/a", "na"}:
            return None
        try:
            value = json.loads(text)
        except json.JSONDecodeError:
            return None
    if not isinstance(value, list):
        return None
    ids: list[int] = []
    for item in value:
        try:
            ids.append(int(item))
        except (TypeError, ValueError):
            continue
    return ids or None


def _policy_from_payload(
    payload: object,
    *,
    raw_response: str | None = None,
    source_url: str | None = None,
    source_text: str | None = None,
) -> PolicyExtractResponse | ExtractionError:
    if not isinstance(payload, dict):
        return ExtractionError(
            message="LLM policy response must be a JSON object.",
            reason="invalid_payload_type",
            raw_response=truncate_raw_response(raw_response),
        )

    methods_raw = payload.get("methods", [])
    if methods_raw is None:
        methods_raw = []
    if not isinstance(methods_raw, list):
        return ExtractionError(
            message="LLM policy response field 'methods' must be an array.",
            reason="invalid_methods_type",
            raw_response=truncate_raw_response(raw_response),
        )

    methods: list[PolicyMethod] = []
    for item in methods_raw:
        if not isinstance(item, dict):
            continue
        code = _nullable_str(item.get("code"))
        name = _nullable_str(item.get("name"))
        purpose = _nullable_str(item.get("purpose"))
        status = _nullable_regulatory_status(item.get("status"))
        if not code and not name:
            continue
        methods.append(
            PolicyMethod(
                code=code or "n/a",
                name=name or code or "n/a",
                purpose=purpose,
                status=status,
            )
        )

    document_name = _nullable_str(payload.get("document_name")) or _nullable_str(
        payload.get("citation")
    )
    if not document_name:
        raw_citation = payload.get("doc_citation")
        if isinstance(raw_citation, dict):
            document_name = _nullable_str(raw_citation.get("en-us")) or _nullable_str(
                raw_citation.get("pt-br")
            )
        else:
            document_name = _nullable_str(raw_citation)

    url = _nullable_str(payload.get("url"))
    if not url and source_text:
        url_match = re.search(
            r"https?://[^\s<>\"']+",
            source_text,
            flags=re.IGNORECASE,
        )
        if url_match:
            url = url_match.group(0).rstrip(".,);]")
    if not url:
        url = _nullable_str(source_url)

    description = _nullable_str(payload.get("description"))
    if not description:
        raw_description = payload.get("doc_description")
        if isinstance(raw_description, dict):
            description = _nullable_str(raw_description.get("en-us")) or _nullable_str(
                raw_description.get("pt-br")
            )
        else:
            description = _nullable_str(raw_description)
    if description and len(description) > _DESCRIPTION_MAX_CHARS:
        description = description[:_DESCRIPTION_MAX_CHARS].rstrip()

    document_name = prefer_oecd_tg_citation(document_name, source_text)

    return PolicyExtractResponse(
        methods=methods,
        document_name=document_name,
        document_date=_nullable_str(payload.get("document_date")),
        responsible_institution=_nullable_str(
            payload.get("responsible_institution")
        ),
        url=url,
        description=description,
    )


def _slugify_method(value: str) -> str:
    slug = re.sub(r"[^a-z0-9]+", "-", value.lower()).strip("-")
    return slug[:80]


def _normalize_oecd_ref(value: str | None) -> str | None:
    if not value:
        return None
    match = re.search(r"\b(?:OECD\s+)?(TG|GD)\s*(\d{3,4}[A-Z]?)\b", value, re.I)
    if match:
        return f"{match.group(1).upper()} {match.group(2).upper()}"
    return value.strip()[:40]


def _ensure_oecd_slug(slug: str | None, oecd_ref: str | None) -> str | None:
    if not slug:
        return None
    cleaned = _slugify_method(slug)
    if oecd_ref and not cleaned.startswith("oecd-"):
        cleaned = f"oecd-{cleaned}"
    return cleaned[:80]


def _string_list(value: object) -> list[str]:
    if value is None:
        return []
    if isinstance(value, str):
        text = value.strip()
        return [text] if text else []
    if not isinstance(value, list):
        return []
    items: list[str] = []
    for item in value:
        text = _nullable_str(item)
        if text:
            items.append(text)
    return items


def _localized_str_from_payload(
    payload: dict,
    field: str,
    legacy_en: str,
    legacy_pt: str,
):
    raw = payload.get(field)
    if isinstance(raw, dict):
        try:
            parsed = parse_localized_str(raw, required=False)
            if parsed is None:
                return None
            if not parsed.en_us.strip() and not parsed.pt_br.strip():
                return None
            return parsed
        except (TypeError, ValueError):
            pass
    if isinstance(raw, str):
        text = _nullable_str(raw)
        return localized_str(text) if text else None
    en = _nullable_str(payload.get(legacy_en))
    pt = _nullable_str(payload.get(legacy_pt)) or en
    if en is None and pt is None:
        return None
    return localized_str(en or pt or "", pt or en or "")


def _enum_or_none(value: object, allowed: frozenset[str]) -> str | None:
    text = _nullable_str(value)
    if text is None:
        return None
    normalized = text.lower().replace(" ", "_").replace("-", "_")
    if normalized in allowed:
        return normalized
    if text in allowed:
        return text
    return None


def _routes_or_none(value: object) -> list[str] | None:
    return coerce_route_list(value)


def _enum_list_or_none(value: object, allowed: frozenset[str]) -> list[str] | None:
    if value is None:
        return None
    if isinstance(value, str):
        text = value.strip()
        if not text:
            return None
        if text.startswith("["):
            try:
                parsed = json.loads(text)
                value = parsed if isinstance(parsed, list) else [text]
            except json.JSONDecodeError:
                value = [text]
        else:
            value = [text]
    if not isinstance(value, list):
        return None
    items: list[str] = []
    for item in value:
        code = _enum_or_none(item, allowed)
        if code and code not in items:
            items.append(code)
    return items or None


def _document_categories_or_none(
    value: object,
    *,
    category_hint: str | None = None,
) -> list[str] | None:
    raw_items: list[object]
    if value is None:
        raw_items = []
    elif isinstance(value, str):
        text = value.strip()
        if not text:
            raw_items = []
        elif text.startswith("["):
            try:
                parsed = json.loads(text)
                raw_items = parsed if isinstance(parsed, list) else [text]
            except json.JSONDecodeError:
                raw_items = [text]
        else:
            raw_items = [text]
    elif isinstance(value, list):
        raw_items = list(value)
    else:
        raw_items = []

    categories: list[str] = []
    for item in raw_items:
        code = _enum_or_none(item, _DOCUMENT_CATEGORY_VALUES)
        if code and code not in categories:
            categories.append(code)

    if not categories and category_hint in _DOCUMENT_CATEGORY_VALUES:
        categories = [category_hint]

    return categories or None


def _method_draft_from_payload(
    payload: object,
    *,
    raw_response: str | None = None,
) -> MethodDraftExtractResponse | ExtractionError:
    if not isinstance(payload, dict):
        return ExtractionError(
            message="LLM method-draft response must be a JSON object.",
            reason="invalid_payload_type",
            raw_response=truncate_raw_response(raw_response),
        )

    oecd_ref = _normalize_oecd_ref(_nullable_str(payload.get("oecd_ref")))
    source_db = _nullable_str(payload.get("source_db"))
    if source_db not in _SOURCE_DB_VALUES:
        source_db = "OECD_TG" if oecd_ref else None

    name = _localized_str_from_payload(payload, "name", "name_en", "name_pt")
    description = _localized_str_from_payload(
        payload, "description", "description_en", "description_pt"
    )
    name_en = name.en_us if name else None
    description_en = description.en_us if description else None

    slug = _ensure_oecd_slug(_nullable_str(payload.get("slug")), oecd_ref)
    if not slug and (oecd_ref or name_en):
        seed = f"oecd-{oecd_ref}-{name_en}" if oecd_ref else name_en or ""
        slug = _ensure_oecd_slug(seed, oecd_ref)

    endpoint = _enum_or_none(payload.get("endpoint_category"), _ENDPOINT_CATEGORY_VALUES)
    application = coerce_application(
        payload.get("application") or payload.get("study_domain")
    )
    text_for_embedding = _nullable_str(payload.get("text_for_embedding"))
    if not text_for_embedding:
        text_for_embedding = " — ".join(
            part for part in (oecd_ref, name_en, description_en) if part
        ) or None

    keywords_raw = payload.get("keywords")
    if isinstance(keywords_raw, dict):
        keywords = localized_str_list(
            _string_list(keywords_raw.get("en-us") or keywords_raw.get("en_us")),
            _string_list(keywords_raw.get("pt-br") or keywords_raw.get("pt_br")),
        )
    else:
        keywords = localized_str_list(
            _string_list(payload.get("keywords_en")),
            _string_list(payload.get("keywords_pt")),
        )

    fields = MethodDraftFields(
        slug=slug,
        name=name,
        description=description,
        animal_use=_enum_or_none(payload.get("animal_use"), _ANIMAL_USE_VALUES),  # type: ignore[arg-type]
        test_system=_enum_list_or_none(  # type: ignore[arg-type]
            payload.get("test_system"), _TEST_SYSTEM_VALUES
        ),
        endpoint_category=endpoint,  # type: ignore[arg-type]
        routes_applicable=_routes_or_none(payload.get("routes_applicable")),  # type: ignore[arg-type]
        application=application,
        oecd_ref=oecd_ref,
        ncit_id=_nullable_str(payload.get("ncit_id")),
        source_citation=_nullable_str(payload.get("source_citation")),
        source_db=source_db,  # type: ignore[arg-type]
        replacement_rationale=_localized_str_from_payload(
            payload,
            "replacement_rationale",
            "replacement_rationale_en",
            "replacement_rationale_pt",
        ),
        reduction_rationale=_localized_str_from_payload(
            payload,
            "reduction_rationale",
            "reduction_rationale_en",
            "reduction_rationale_pt",
        ),
        refinement_rationale=_localized_str_from_payload(
            payload,
            "refinement_rationale",
            "refinement_rationale_en",
            "refinement_rationale_pt",
        ),
        keywords=keywords,
        text_for_embedding=text_for_embedding,
        active=False,
    )
    return MethodDraftExtractResponse(fields=fields)


def _truncate_localized(value, *, max_chars: int):
    if value is None:
        return None
    en = (value.en_us or "")[:max_chars]
    pt = (value.pt_br or "")[:max_chars]
    if not en and not pt:
        return None
    return localized_str(en or pt, pt or en)


def _document_draft_from_payload(
    payload: object,
    *,
    category_hint: str | None = None,
    source_url: str | None = None,
    source_text: str | None = None,
    raw_response: str | None = None,
) -> DocumentDraftExtractResponse | ExtractionError:
    if not isinstance(payload, dict):
        return ExtractionError(
            message="LLM document-draft response must be a JSON object.",
            reason="invalid_payload_type",
            raw_response=truncate_raw_response(raw_response),
        )

    citation = _localized_str_from_payload(
        payload, "doc_citation", "citation_en", "citation_pt"
    )
    if citation is None:
        citation = _localized_str_from_payload(
            payload, "citation", "citation_en", "citation_pt"
        )

    citation_en = citation.en_us if citation else None
    preferred = prefer_oecd_tg_citation(citation_en, source_text)
    if preferred:
        citation = localized_str(preferred)

    description = _truncate_localized(
        _localized_str_from_payload(
            payload, "description", "description_en", "description_pt"
        ),
        max_chars=_DESCRIPTION_MAX_CHARS,
    )

    categories = _document_categories_or_none(
        payload.get("categories", payload.get("category")),
        category_hint=category_hint,
    )

    institution = _localized_str_from_payload(
        payload,
        "institution",
        "institution_en",
        "institution_pt",
    )

    slug = _nullable_str(payload.get("slug"))
    if slug:
        slug = _slugify_method(slug)[:80] or None
    elif citation and citation.en_us:
        slug = _slugify_method(citation.en_us)[:80] or None

    url = _nullable_str(payload.get("url")) or _nullable_str(source_url)

    date = _nullable_str(payload.get("date"))
    if date and re.fullmatch(r"20\d{2}", date):
        date = f"{date}-01-01"

    fields = DocumentDraftFields(
        slug=slug,
        date=date,
        url=url,
        categories=categories,  # type: ignore[arg-type]
        institution=institution,
        doc_citation=citation,
        description=description,
    )
    return DocumentDraftExtractResponse(fields=fields)


def _regulation_draft_from_payload(
    payload: object,
    *,
    raw_response: str | None = None,
) -> RegulationDraftExtractResponse | ExtractionError:
    if not isinstance(payload, dict):
        return ExtractionError(
            message="LLM regulation-draft response must be a JSON object.",
            reason="invalid_payload_type",
            raw_response=truncate_raw_response(raw_response),
        )

    jurisdiction = None
    raw_jurisdiction = payload.get("jurisdiction")
    if raw_jurisdiction is not None:
        try:
            if isinstance(raw_jurisdiction, str):
                mapped = jurisdiction_for_code(raw_jurisdiction)
                jurisdiction = mapped or parse_jurisdiction(raw_jurisdiction)
            else:
                jurisdiction = parse_jurisdiction(raw_jurisdiction)
        except (TypeError, ValueError):
            jurisdiction = None

    date = _nullable_str(
        payload.get("regulatory_date") or payload.get("regulation_date")
    )
    if date and re.fullmatch(r"20\d{2}", date):
        date = f"{date}-01-01"

    fields = RegulationDraftFields(
        jurisdiction=jurisdiction,
        regulatory_status=_nullable_regulatory_status(
            payload.get("regulatory_status") or payload.get("regulation_status")
        ),
        regulatory_date=date,
        regulatory_endpoints=_int_list_from_payload(
            payload.get("regulatory_endpoints")
        ),
        endpoint_quote=_nullable_str(payload.get("endpoint_quote")),
        regulatory_body=_localized_str_from_payload(
            payload, "regulatory_body", "regulatory_body_en", "regulatory_body_pt"
        ),
        regulatory_citation=_localized_str_from_payload(
            payload,
            "regulatory_citation",
            "regulatory_citation_en",
            "regulatory_citation_pt",
        ),
        notes=_nullable_str(payload.get("notes")),
    )
    return RegulationDraftExtractResponse(fields=fields)
  
def build_llm_adapter(
    *,
    model: str,
    use_stub: bool,
    ollama_model: str | None = None,
) -> LLMAdapter:
    if ollama_model:
        return OllamaLLMAdapter(model=ollama_model)
