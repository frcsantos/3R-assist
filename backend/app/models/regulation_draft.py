from typing import Literal

from pydantic import BaseModel, Field, field_validator, model_validator

from app.models.i18n import LocalizedStr
from app.models.method import RegulatoryStatus
from app.models.policy import looks_like_single_url


class RegulationDraftExtractRequest(BaseModel):
    text: str = Field(..., min_length=1, max_length=50000)
    source_url: str | None = Field(default=None, max_length=2000)
    lang: Literal["pt", "en"] | None = None

    @field_validator("text")
    @classmethod
    def strip_text(cls, value: str) -> str:
        return value.strip()

    @model_validator(mode="after")
    def require_length_unless_url(self) -> "RegulationDraftExtractRequest":
        if looks_like_single_url(self.text):
            return self
        if len(self.text) < 20:
            raise ValueError("text must be at least 20 characters unless it is a URL")
        return self


class RegulationDraftFields(BaseModel):
    jurisdiction: LocalizedStr | None = None
    regulation_status: RegulatoryStatus | None = None
    regulation_date: str | None = None
    regulation_purpose: str | None = None
    regulatory_body: str | None = None
    regulatory_citation: str | None = None
    notes: str | None = None


class RegulationDraftExtractResponse(BaseModel):
    fields: RegulationDraftFields
