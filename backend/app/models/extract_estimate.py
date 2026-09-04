from typing import Literal

from pydantic import BaseModel, Field, field_validator, model_validator

from app.models.document_draft import DocumentCategory
from app.models.policy import looks_like_single_url

ExtractMode = Literal["policy", "document"]


class ExtractEstimateRequest(BaseModel):
    text: str = Field(..., min_length=1, max_length=50000)
    mode: ExtractMode = "policy"
    category_hint: DocumentCategory | None = None
    source_url: str | None = Field(default=None, max_length=2000)
    lang: Literal["pt", "en"] | None = None

    @field_validator("text")
    @classmethod
    def strip_text(cls, value: str) -> str:
        return value.strip()

    @model_validator(mode="after")
    def require_length_unless_url(self) -> "ExtractEstimateRequest":
        if looks_like_single_url(self.text):
            return self
        if len(self.text) < 20:
            raise ValueError("text must be at least 20 characters unless it is a URL")
        return self


class ExtractEstimateResponse(BaseModel):
    model: str
    input_tokens: int
    output_tokens: int
    estimated_cost_usd: float


class ExtractResolveRequest(BaseModel):
    text: str = Field(..., min_length=1, max_length=50000)

    @field_validator("text")
    @classmethod
    def strip_text(cls, value: str) -> str:
        return value.strip()


class ExtractResolveResponse(BaseModel):
    text: str = Field(..., min_length=1, max_length=50000)
    source_url: str | None = None
    fetched: bool = False
