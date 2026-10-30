from pydantic import BaseModel, Field

from app.models.method import Method, MethodRegulatoryContext


class Recommendation(BaseModel):
    method: Method
    regulatory_contexts: list[MethodRegulatoryContext] = Field(default_factory=list)
    rank: int
    score: float
    matched_params: list[str]
    # Weighted components behind `score` (component name -> 0..1); only those that applied.
    score_breakdown: dict[str, float] = Field(default_factory=dict)
