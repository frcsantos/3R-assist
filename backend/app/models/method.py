from datetime import date, datetime
from typing import Literal

from pydantic import BaseModel, Field, computed_field, field_validator

from app.models.i18n import LocalizedStr, LocalizedStrList
from app.models.jurisdiction import parse_jurisdiction

ThreeRClass = Literal["replacement", "reduction", "refinement"]
StudyDomain = Literal["pharma", "cosmetics", "chemical_safety", "general"]
ValidationStatus = Literal[
    "validated",
    "in_process_of_validation",
    "not_validated",
]
RegulatoryStatus = Literal["not_approved", "approved", "recommended", "mandatory"]
# Preferred curated values: OECD_TG | ECVAM_DBALM | NICEATM | FARMACOPEIA_BR | TSAR.
# Stored as free text so admin-curated / imported rows are not rejected at read time.
SourceDb = str

_THREE_R_ORDER: tuple[ThreeRClass, ...] = ("replacement", "reduction", "refinement")


class MethodRegulatoryContext(BaseModel):
    jurisdiction: LocalizedStr
    validation_status: ValidationStatus
    regulation_status: RegulatoryStatus | None = None
    regulation_date: date | None = None
    regulation_purpose: str | None = None
    regulatory_body: str | None = None
    regulatory_doc_id: int | None = None
    regulatory_citation: str | None = None
    # Resolved from documents.url when regulatory_doc_id is set (not a DB column).
    regulatory_url: str | None = None
    notes: str | None = None

    @field_validator("jurisdiction", mode="before")
    @classmethod
    def _coerce_jurisdiction(cls, value):
        return parse_jurisdiction(value)


class Method(BaseModel):
    id: int
    slug: str
    active: bool = False
    name: LocalizedStr
    description: LocalizedStr
    endpoint_category: str
    routes_applicable: list[str] | None = None
    study_domain: StudyDomain
    oecd_ref: str | None = None
    ncit_id: str | None = None
    source_citation: str | None = None
    source_doc_id: int | None = None
    # Resolved from documents.url when source_doc_id is set (not a DB column).
    source_url: str | None = None
    source_db: SourceDb
    replacement_rationale: str | None = None
    reduction_rationale: str | None = None
    refinement_rationale: str | None = None
    keywords: LocalizedStrList = Field(default_factory=LocalizedStrList)
    text_for_embedding: str
    embedding_json: list[float] | None = None
    created_at: datetime | None = None
    updated_at: datetime | None = None

    @staticmethod
    def _nonempty(value: str | None) -> bool:
        return value is not None and value.strip() != ""

    def rationale_for(self, value: ThreeRClass) -> str | None:
        field = f"{value}_rationale"
        text = getattr(self, field)
        return text if self._nonempty(text) else None

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
