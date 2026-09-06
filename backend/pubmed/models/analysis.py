from __future__ import annotations

from typing import Literal

from pydantic import BaseModel, Field

from app.models.protocol import (
    ConfidenceLevel,
    EndpointCategory,
    ProtocolParameters,
    ThreeRClass,
)
from pubmed.models.record import PubMedRecord

NecessityVerdictType = Literal["necessary", "possibly_avoidable", "not_necessary"]


class NecessityAssessment(BaseModel):
    verdict: NecessityVerdictType
    confidence: ConfidenceLevel
    rationale: str
    key_concerns: list[str] = Field(default_factory=list)
    suggested_approach: str | None = None


class LLMProposedAlternative(BaseModel):
    """An alternative method proposed by the LLM based on its domain knowledge.

    Always returned regardless of whether literature evidence was found.
    Marked as LLM-proposed so the consumer can distinguish it from
    literature-backed recommendations.
    """
    three_r_class: ThreeRClass
    method_description: str


class PubMedRecommendation(BaseModel):
    """A literature-backed recommendation retrieved from the PubMed knowledge base."""
    record: PubMedRecord
    relevance_score: float          # cosine × three_r_weight
    relevance_explanation: str
    three_r_class: ThreeRClass
    endpoint_category: EndpointCategory | None = None
    rank: int


class Citation(BaseModel):
    """Structured bibliographic reference for an article cited in the summary."""
    pmid: str
    title: str
    authors_display: str    # "Smith J, Jones A, Brown B, et al."
    pub_year: int | None = None


class PubMedAnalyzeRequest(BaseModel):
    protocol_text: str = Field(..., min_length=20, max_length=40_000)
    params: ProtocolParameters | None = None
    lang: Literal["pt", "en"] | None = None


class PubMedAnalysisResponse(BaseModel):
    necessity: NecessityAssessment | None = None
    endpoint_hypothesis: str | None = None
    recommendations: list[PubMedRecommendation] = Field(default_factory=list)
    summary: str | None = None
    citations: list[Citation] = Field(default_factory=list)
    no_literature_found: bool = False
    total_candidates_searched: int = 0
