from typing import Literal

from pydantic import BaseModel, Field, field_validator, model_validator

from app.models.i18n import LocalizedStr
from app.models.policy import looks_like_single_url

DocumentCategory = Literal["method_protocol", "guideline", "regulation", "other"]


class DocumentDraftExtractRequest(BaseModel):
    text: str = Field(..., min_length=1, max_length=50000)
    category_hint: DocumentCategory | None = None
    source_url: str | None = Field(default=None, max_length=2000)
    lang: Literal["pt", "en"] | None = None

    @field_validator("text")
    @classmethod
    def strip_text(cls, value: str) -> str:
        return value.strip()

    @model_validator(mode="after")
    def require_length_unless_url(self) -> "DocumentDraftExtractRequest":
        if looks_like_single_url(self.text):
            return self
        if len(self.text) < 20:
            raise ValueError("text must be at least 20 characters unless it is a URL")
        return self


class DocumentDraftFields(BaseModel):
    slug: str | None = None
    date: str | None = None
    url: str | None = None
    category: DocumentCategory | None = None
    doc_citation: LocalizedStr | None = None
    description: LocalizedStr | None = None


class DocumentDraftExtractResponse(BaseModel):
    fields: DocumentDraftFields
