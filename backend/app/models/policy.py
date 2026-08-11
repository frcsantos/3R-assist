from typing import Literal

from pydantic import BaseModel, Field, field_validator, model_validator

from app.models.i18n import LocalizedStr
from app.models.method import MethodRegulatoryContext, RegulatoryStatus


def _looks_like_single_url(text: str) -> bool:
    candidate = text.strip()
    if not candidate or any(ch.isspace() for ch in candidate):
        return False
    lower = candidate.lower()
    return lower.startswith(("http://", "https://", "www."))


def looks_like_single_url(text: str) -> bool:
    """True when `text` is a single URL-like token (http(s) or www.)."""
    return _looks_like_single_url(text)


class PolicyMethod(BaseModel):
    code: str
    name: str
    purpose: str | None = None
    status: RegulatoryStatus | None = None


class PolicyExtractRequest(BaseModel):
    text: str = Field(..., min_length=1, max_length=50000)
    lang: Literal["pt", "en"] | None = None
    source_url: str | None = Field(default=None, max_length=2000)

    @field_validator("text")
    @classmethod
    def strip_text(cls, value: str) -> str:
        return value.strip()

    @field_validator("source_url")
    @classmethod
    def strip_source_url(cls, value: str | None) -> str | None:
        if value is None:
            return None
        cleaned = value.strip()
        return cleaned or None

    @model_validator(mode="after")
    def require_length_unless_url(self) -> "PolicyExtractRequest":
        if _looks_like_single_url(self.text):
            return self
        if len(self.text) < 20:
            raise ValueError("text must be at least 20 characters unless it is a URL")
        return self


class PolicyExtractResponse(BaseModel):
    methods: list[PolicyMethod] = Field(default_factory=list)
    document_name: str | None = None
    document_date: str | None = None
    responsible_institution: str | None = None
    url: str | None = None
    description: str | None = None


class PolicyMethodMatchRequest(BaseModel):
    code: str = Field(..., min_length=1, max_length=200)
    name: str = Field(..., min_length=1, max_length=500)
    purpose: str | None = Field(default=None, max_length=1000)
    limit: int = Field(default=5, ge=1, le=20)


class MatchedMethodSummary(BaseModel):
    id: int
    slug: str
    name: LocalizedStr
    description: LocalizedStr
    text_for_embedding: str
    endpoint_category: str
    study_domain: str
    oecd_ref: str | None = None
    source_db: str
    validation_status: str = "not_evaluated"
    active: bool
    regulatory_contexts: list[MethodRegulatoryContext] = Field(default_factory=list)


class PolicyMethodMatchCandidate(BaseModel):
    match_kind: Literal["oecd_ref", "text_for_embedding"]
    score: float
    method: MatchedMethodSummary


class PolicyMethodMatchResponse(BaseModel):
    normalized_oecd_ref: str | None = None
    matches: list[PolicyMethodMatchCandidate] = Field(default_factory=list)


class PolicyDocumentMatchRequest(BaseModel):
    document_name: str | None = Field(default=None, max_length=500)
    document_date: str | None = Field(default=None, max_length=40)
    responsible_institution: str | None = Field(default=None, max_length=500)
    url: str | None = Field(default=None, max_length=2000)
    limit: int = Field(default=5, ge=1, le=20)


class MatchedDocumentSummary(BaseModel):
    id: int
    slug: str
    doc_citation: LocalizedStr
    date: str | None = None
    categories: list[str] = Field(default_factory=list)
    institution: LocalizedStr | None = None
    url: str | None = None


class PolicyDocumentMatchCandidate(BaseModel):
    match_kind: Literal["doc_citation", "url", "text"]
    score: float
    document: MatchedDocumentSummary


class PolicyDocumentMatchResponse(BaseModel):
    matches: list[PolicyDocumentMatchCandidate] = Field(default_factory=list)
