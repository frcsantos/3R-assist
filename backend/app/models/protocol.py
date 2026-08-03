from __future__ import annotations

from typing import Literal

from pydantic import BaseModel, Field

from app.models.recommendation import Recommendation

ConfidenceLevel = Literal["high", "medium", "low"]

EndpointCategory = Literal[
    "acute_toxicity",
    "skin_irritation",
    "skin_corrosion",
    "ocular_irritation",
    "skin_sensitisation",
    "phototoxicity",
    "genotoxicity",
    "pyrogenicity",
    "skin_absorption",
]

Route = Literal[
    "oral",
    "intraperitoneal",
    "intravenous",
    "dermal",
    "ocular",
    "inhalation",
    "in_vitro",
    "other",
]

StudyDomain = Literal["pharma", "cosmetics", "chemical_safety", "general"]

Species = Literal[
    "rat",
    "mouse",
    "rabbit",
    "guinea_pig",
    "chicken",
    "zebrafish",
    "in_vitro",
    "other",
]


class AnimalCounts(BaseModel):
    female: int | None = None
    male: int | None = None
    total: int | None = None
    per_group: int | None = None


class RawExtraction(BaseModel):
    study_type: str
    route: list[Route] | None = None
    route_evidence: str | None = None
    route_confidence: ConfidenceLevel | None = None
    study_domain: StudyDomain = "general"
    study_domain_evidence: str | None = None
    study_domain_confidence: ConfidenceLevel | None = None
    procedure_text: str | None = None
    procedure_text_evidence: str | None = None
    procedure_text_confidence: ConfidenceLevel | None = None
    species: Species | None = None
    species_evidence: str | None = None
    species_confidence: ConfidenceLevel | None = None
    animal_counts: AnimalCounts | None = None
    animal_counts_evidence: str | None = None
    animal_counts_confidence: ConfidenceLevel | None = None
    regulatory: bool | None = None
    regulatory_evidence: str | None = None
    regulatory_confidence: ConfidenceLevel | None = None
    notes: str | None = None


class ExtractionResult(BaseModel):
    raw: RawExtraction
    endpoint_category: EndpointCategory | None = None


class ProtocolParameters(BaseModel):
    """Flattened view used by retrieval and legacy API fields."""

    endpoint_category: EndpointCategory | None = None
    route: list[Route] | None = None
    study_domain: StudyDomain = "general"
    procedure_text: str | None = None
    species: Species | None = None
    n_animals: int | None = None
    regulatory: bool | None = None

    def has_extractable_content(self) -> bool:
        return self.endpoint_category is not None or bool(self.procedure_text)


def primary_animal_count(counts: AnimalCounts | None) -> int | None:
    if counts is None:
        return None
    if counts.total is not None:
        return counts.total
    if counts.male is not None and counts.female is not None:
        return counts.male + counts.female
    return counts.male or counts.female or counts.per_group


def to_protocol_parameters(result: ExtractionResult) -> ProtocolParameters:
    return ProtocolParameters(
        endpoint_category=result.endpoint_category,
        route=result.raw.route,
        study_domain=result.raw.study_domain,
        procedure_text=result.raw.procedure_text,
        species=result.raw.species,
        n_animals=primary_animal_count(result.raw.animal_counts),
        regulatory=result.raw.regulatory,
    )


class AnalyzeRequest(BaseModel):
    protocol_text: str = Field(..., min_length=20, max_length=40000)
    lang: Literal["pt", "en"] | None = None


class ExperimentResult(BaseModel):
    raw: RawExtraction
    endpoint_category: EndpointCategory | None = None
    params: ProtocolParameters
    notes: str | None = None

    @classmethod
    def from_extraction(cls, result: ExtractionResult) -> ExperimentResult:
        return cls(
            raw=result.raw,
            endpoint_category=result.endpoint_category,
            params=to_protocol_parameters(result),
            notes=result.raw.notes,
        )


class AnalyzeResponse(BaseModel):
    experiments: list[ExperimentResult] = Field(..., min_length=1)
    params: ProtocolParameters


ThreeRClass = Literal["replacement", "reduction", "refinement"]
JurisdictionFilter = Literal["brazil", "eu", "us", "oecd"]


class SearchFilters(BaseModel):
    three_r_class: ThreeRClass | None = None
    jurisdiction: JurisdictionFilter | None = None
    endpoint: EndpointCategory | None = None


class SearchRequest(BaseModel):
    params: ProtocolParameters
    filters: SearchFilters | None = None
    lang: Literal["pt", "en"] | None = None


class SearchResponse(BaseModel):
    query_id: int | None = None
    results: list[Recommendation] = Field(default_factory=list)
    filter_relaxation: str | None = None
