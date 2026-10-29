import json
from datetime import date, datetime
from typing import Literal

from pydantic import BaseModel, Field, computed_field, field_validator

from app.models.i18n import LocalizedStr, LocalizedStrList, localized_str, parse_localized_str
from app.models.jurisdiction import parse_jurisdiction

ThreeRClass = Literal["replacement", "reduction", "refinement"]
AnimalUse = Literal[
    "none",
    "animal_derived_material",
    "slaughterhouse_byproduct",
    "animals_killed_for_tissue",
    "live_animals",
    "mixed_or_variable",
    "embryos_and_larvae",
]
TestSystem = Literal[
    "in_silico",
    "in_chemico",
    "in_data",
    "in_vitro",
    "ex_vivo",
    "in_vivo",
    "unclear",
]
ValidationStatus = Literal[
    "recognized",
    "under_validation",
    "validated",
    "partially_validated",
    "not_validated",
    "unclear",
]
RegulatoryStatus = Literal[
    "not_approved", "approved", "recognized", "adopted", "published",
    "recommended", "mandatory"
]
# Preferred curated values: OECD_TG | ECVAM_DBALM | NICEATM | FARMACOPEIA_BR | TSAR.
# Stored as free text so admin-curated / imported rows are not rejected at read time.
SourceDb = str

_THREE_R_ORDER: tuple[ThreeRClass, ...] = ("replacement", "reduction", "refinement")


class MethodRegulatoryContext(BaseModel):
    id: int | None = None
    jurisdiction: LocalizedStr
    regulatory_status: RegulatoryStatus | None = None
    regulatory_date: date | None = None
    published_date: date | None = None
    effective_date: date | None = None
    replacement_term_years: int | None = None
    # Generated column: effective_date + replacement_term_years.
    replacement_deadline: date | None = None
    regulatory_endpoints: list[int] | None = None
    # Resolved from endpoints.name for regulatory_endpoints (not a DB column).
    regulatory_endpoint_names: list[LocalizedStr] = Field(default_factory=list)
    endpoint_quote: str | None = None
    regulatory_body: LocalizedStr | None = None
    regulatory_doc_id: int | None = None
    regulatory_citation: LocalizedStr | None = None
    # Verbatim passage of the regulation (regulations.regulatory_quote); the
    # regulatory_citation above falls back to the document citation when empty.
    regulatory_quote: LocalizedStr | None = None
    # Resolved from documents.doc_citation when regulatory_doc_id is set.
    document_citation: LocalizedStr | None = None
    # Resolved from documents.url when regulatory_doc_id is set (not a DB column).
    regulatory_url: str | None = None
    notes: str | None = None

    @field_validator("jurisdiction", mode="before")
    @classmethod
    def _coerce_jurisdiction(cls, value):
        return parse_jurisdiction(value)

    @field_validator("regulatory_endpoints", mode="before")
    @classmethod
    def _coerce_endpoint_ids(cls, value):
        if value is None:
            return None
        if isinstance(value, str) and not value.strip():
            return None
        if isinstance(value, str):
            value = json.loads(value)
        if isinstance(value, (tuple, list)):
            return [int(item) for item in value]
        raise TypeError(f"Unsupported regulatory_endpoints value: {type(value)!r}")

    @field_validator("regulatory_endpoint_names", mode="before")
    @classmethod
    def _coerce_endpoint_names(cls, value):
        if value is None:
            return []
        if isinstance(value, str) and not value.strip():
            return []
        if not isinstance(value, list):
            return []
        names: list[LocalizedStr] = []
        for item in value:
            parsed = parse_localized_str(item, required=False)
            if parsed is None:
                continue
            if not parsed.en_us.strip() and not parsed.pt_br.strip():
                continue
            names.append(parsed)
        return names

    @field_validator(
        "regulatory_body",
        "regulatory_citation",
        "regulatory_quote",
        "document_citation",
        mode="before",
    )
    @classmethod
    def _coerce_localized(cls, value):
        if value is None:
            return None
        if isinstance(value, str) and not value.strip():
            return None
        if isinstance(value, str) and not value.strip().startswith("{"):
            return localized_str(value)
        parsed = parse_localized_str(value, required=False)
        if parsed is None:
            return None
        if not parsed.en_us.strip() and not parsed.pt_br.strip():
            return None
        return parsed


ReviewStatus = Literal["not_reviewed", "in_review", "reviewed"]


class MethodMaterial(BaseModel):
    """Biological material or system used by a method (method_materials row)."""

    kind: str
    name: LocalizedStr
    species_slug: str | None = None
    species_name: LocalizedStr | None = None
    origin: str | None = None
    animal_derived: bool | None = None
    notes: str | None = None

    @field_validator("name", "species_name", mode="before")
    @classmethod
    def _coerce_localized(cls, value):
        if value is None:
            return None
        if isinstance(value, str) and value.strip().startswith("{"):
            value = json.loads(value)
        return parse_localized_str(value, required=False)


class Method(BaseModel):
    id: int
    slug: str
    active: bool = False
    name: LocalizedStr
    description: LocalizedStr
    animal_use: AnimalUse | None = None
    test_system: list[TestSystem] | None = None
    endpoints: list[int] = Field(default_factory=list)
    # Resolved from endpoints.slug for methods.endpoints (not a DB column).
    endpoint_codes: list[str] = Field(default_factory=list)
    endpoint_names: list[LocalizedStr] = Field(default_factory=list)
    routes_applicable: list[int] | None = None
    # Resolved from routes.slug for methods.routes_applicable (not a DB column).
    route_codes: list[str] = Field(default_factory=list)
    route_names: list[LocalizedStr] = Field(default_factory=list)
    application_ids: list[int] = Field(default_factory=list)
    # Resolved from applications.slug for methods.application_ids (not a DB column).
    application_codes: list[str] = Field(default_factory=list)
    application_names: list[LocalizedStr] = Field(default_factory=list)
    oecd_ref: str | None = None
    source_citation: str | None = None
    source_doc_id: int | None = None
    # Resolved from documents.url when source_doc_id is set (not a DB column).
    source_url: str | None = None
    source_db: SourceDb
    validation_status: ValidationStatus | None = None
    validation_doc_id: int | None = None
    # Resolved from documents.url when validation_doc_id is set (not a DB column).
    validation_url: str | None = None
    replacement_rationale: LocalizedStr | None = None
    reduction_rationale: LocalizedStr | None = None
    refinement_rationale: LocalizedStr | None = None
    review_status: ReviewStatus = "not_reviewed"
    # [{name, species, oecd_ref, r_type, extent, note}] (methods.animal_procedures_avoided).
    animal_procedures_avoided: list[dict] = Field(default_factory=list)
    materials: list[MethodMaterial] = Field(default_factory=list)
    keywords: LocalizedStrList = Field(default_factory=LocalizedStrList)
    text_for_embedding: str
    embedding_json: list[float] | None = None
    created_at: datetime | None = None
    updated_at: datetime | None = None

    @field_validator("endpoints", "application_ids", mode="before")
    @classmethod
    def _coerce_method_endpoint_ids(cls, value):
        if value is None:
            return []
        if isinstance(value, str) and not value.strip():
            return []
        if isinstance(value, str):
            value = json.loads(value)
        if isinstance(value, int):
            return [value]
        if isinstance(value, (tuple, list)):
            return [int(item) for item in value]
        raise TypeError(f"Unsupported integer-array value: {type(value)!r}")

    @field_validator("animal_procedures_avoided", "materials", mode="before")
    @classmethod
    def _coerce_json_lists(cls, value):
        if value is None:
            return []
        if isinstance(value, str):
            text = value.strip()
            return json.loads(text) if text else []
        return value

    @field_validator("routes_applicable", mode="before")
    @classmethod
    def _coerce_route_ids(cls, value):
        if value is None:
            return None
        if isinstance(value, str) and not value.strip():
            return None
        if isinstance(value, str):
            value = json.loads(value)
        if isinstance(value, int):
            return [value]
        if isinstance(value, (tuple, list)):
            return [int(item) for item in value]
        raise TypeError(f"Unsupported routes_applicable value: {type(value)!r}")

    @field_validator("endpoint_codes", "route_codes", "application_codes", mode="before")
    @classmethod
    def _coerce_endpoint_codes(cls, value):
        if value is None:
            return []
        if isinstance(value, str):
            text = value.strip()
            return [text] if text else []
        if isinstance(value, (tuple, list)):
            return [str(item) for item in value if str(item).strip()]
        return []

    @field_validator(
        "endpoint_names", "route_names", "application_names", mode="before"
    )
    @classmethod
    def _coerce_endpoint_names(cls, value):
        if value is None:
            return []
        if isinstance(value, str) and not value.strip():
            return []
        if not isinstance(value, list):
            return []
        names: list[LocalizedStr] = []
        for item in value:
            parsed = parse_localized_str(item, required=False)
            if parsed is None:
                continue
            if not parsed.en_us.strip() and not parsed.pt_br.strip():
                continue
            names.append(parsed)
        return names

    @field_validator(
        "replacement_rationale",
        "reduction_rationale",
        "refinement_rationale",
        mode="before",
    )
    @classmethod
    def _coerce_rationale(cls, value):
        if value is None:
            return None
        if isinstance(value, str) and not value.strip():
            return None
        if isinstance(value, str) and not value.strip().startswith("{"):
            return localized_str(value)
        parsed = parse_localized_str(value, required=False)
        if parsed is None:
            return None
        if not parsed.en_us.strip() and not parsed.pt_br.strip():
            return None
        return parsed

    @staticmethod
    def _nonempty_rationale(value: LocalizedStr | None) -> bool:
        if value is None:
            return False
        return bool(value.en_us.strip() or value.pt_br.strip())

    def rationale_for(self, value: ThreeRClass) -> LocalizedStr | None:
        field = f"{value}_rationale"
        text = getattr(self, field)
        return text if self._nonempty_rationale(text) else None

    def has_three_r(self, value: ThreeRClass) -> bool:
        return self.rationale_for(value) is not None

    @computed_field  # type: ignore[prop-decorator]
    @property
    def category_3r(self) -> list[ThreeRClass]:
        """Derived from non-null/non-empty rationale columns (ADR-023)."""
        return [r for r in _THREE_R_ORDER if self.has_three_r(r)]

    @property
    def primary_three_r(self) -> ThreeRClass:
        for preferred in _THREE_R_ORDER:
            if self.has_three_r(preferred):
                return preferred
        return "replacement"
