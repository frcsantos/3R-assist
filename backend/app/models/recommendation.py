from pydantic import BaseModel, Field

from app.models.method import Method, MethodRegulatoryContext


class Recommendation(BaseModel):
    method: Method
    regulatory_contexts: list[MethodRegulatoryContext] = Field(default_factory=list)
    rank: int
    score: float
    matched_params: list[str]
