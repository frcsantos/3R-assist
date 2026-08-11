from typing import Literal

from pydantic import BaseModel, Field

from app.models.i18n import LocalizedStr, LocalizedStrList
from app.models.method import AnimalUse, TestSystem
from app.models.protocol import EndpointCategory, Route, StudyDomain

SourceDbValue = Literal[
    "OECD_TG",
    "ECVAM_DBALM",
    "NICEATM",
    "FARMACOPEIA_BR",
    "TSAR",
]


class MethodDraftExtractRequest(BaseModel):
    text: str = Field(..., min_length=20, max_length=100000)
    lang: Literal["pt", "en"] | None = None


class MethodDraftFields(BaseModel):
    slug: str | None = None
    name: LocalizedStr | None = None
    description: LocalizedStr | None = None
    animal_use: AnimalUse | None = None
    test_system: list[TestSystem] | None = None
    endpoint_category: EndpointCategory | None = None
    routes_applicable: list[Route] | None = None
    study_domain: StudyDomain | None = None
    oecd_ref: str | None = None
    ncit_id: str | None = None
    source_citation: str | None = None
    source_db: SourceDbValue | None = None
    replacement_rationale: LocalizedStr | None = None
    reduction_rationale: LocalizedStr | None = None
    refinement_rationale: LocalizedStr | None = None
    keywords: LocalizedStrList = Field(default_factory=LocalizedStrList)
    text_for_embedding: str | None = None
    active: bool = False


class MethodDraftExtractResponse(BaseModel):
    fields: MethodDraftFields
