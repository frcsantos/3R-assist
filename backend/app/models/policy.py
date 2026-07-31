from typing import Literal

from pydantic import BaseModel, Field

from app.models.i18n import LocalizedStr
from app.models.method import MethodRegulatoryContext, RegulatoryStatus


class PolicyMethod(BaseModel):
    code: str
    name: str
    purpose: str | None = None
    status: RegulatoryStatus | None = None


class PolicyExtractRequest(BaseModel):
    text: str = Field(..., min_length=20, max_length=50000)
    lang: Literal["pt", "en"] | None = None


class PolicyExtractResponse(BaseModel):
    methods: list[PolicyMethod] = Field(default_factory=list)
    document_name: str | None = None
    document_date: str | None = None
    responsible_institution: str | None = None


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
    category: str
    url: str | None = None


class PolicyDocumentMatchCandidate(BaseModel):
    match_kind: Literal["doc_citation", "url", "text"]
    score: float
    document: MatchedDocumentSummary


class PolicyDocumentMatchResponse(BaseModel):
    matches: list[PolicyDocumentMatchCandidate] = Field(default_factory=list)
