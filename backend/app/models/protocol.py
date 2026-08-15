from __future__ import annotations

from typing import Literal

from pydantic import AliasChoices, BaseModel, ConfigDict, Field, field_validator

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
    "reproductive_toxicity",
    "endocrine_activity",
    "photoreactivity",
    "aquatic_toxicity",
    "toxicokinetics",
    "bacterial_endotoxin",
    "rabies_diagnosis",
]


def normalize_endpoint_slug(value: str | None) -> str | None:
    if value is None:
        return None
    text = str(value).strip()
    if not text:
        return None
    slug = text.replace("_", "-")
    return _ENDPOINT_SLUG_ALIASES.get(slug, slug)


_ENDPOINT_SLUG_ALIASES = {
    "acute-toxicity": "acute-systemic-toxicity",
    "ocular-irritation": "eye-irritation",
    "skin-absorption": "dermal-absorption",
    "bacterial-endotoxin": "bacterial-endotoxins",
    "toxicokinetics": "toxicokinetic-properties",
}

Route = Literal[
    "cutaneous",
    "inhalation",
    "oral",
    "ocular",
    "intranasal",
    "intratracheal",
    "intravenous",
    "intra-arterial",
    "intramuscular",
    "subcutaneous",
    "intradermal",
    "intraperitoneal",
    "rectal",
    "vaginal",
    "topical-mucosal",
    "implantation",
    "multiple",
    "not-applicable",
    "unspecified",
    "other",
]

_ROUTE_SLUGS: frozenset[str] = frozenset(Route.__args__)
_ROUTE_ALIASES = {
    "dermal": "cutaneous",
}


def normalize_route_slug(value: str | None) -> str | None:
    if value is None:
        return None
    text = str(value).strip()
    if not text:
        return None
    slug = text.replace("_", "-")
    slug = _ROUTE_ALIASES.get(slug, slug)
    return slug


def coerce_route_list(value) -> list[str] | None:
    if value is None:
        return None
    if isinstance(value, str) and not value.strip():
        return None
    if isinstance(value, str):
        value = [value]
    if not isinstance(value, (tuple, list)):
        return None
    routes: list[str] = []
    for item in value:
        slug = normalize_route_slug(str(item))
        if slug in _ROUTE_SLUGS and slug not in routes:
            routes.append(slug)
    return routes or None

Application = Literal[
    "basic-research",
    "translational-applied-research",
    "regulatory-use",
    "routine-production",
    "education-training",
    "environmental-protection",
    "species-preservation",
    "forensic-inquiry",
    "other",
]

_APPLICATION_SLUGS: frozenset[str] = frozenset(Application.__args__)
_APPLICATION_ALIASES = {
    "general": "basic-research",
    "pharma": "regulatory-use",
    "cosmetics": "regulatory-use",
    "chemical-safety": "regulatory-use",
    "basic-research": "basic-research",
    "education": "education-training",
}
DEFAULT_APPLICATION: Application = "basic-research"


def normalize_application_slug(value: str | None) -> str | None:
    if value is None:
        return None
    text = str(value).strip()
    if not text:
        return None
    slug = text.replace("_", "-")
    return _APPLICATION_ALIASES.get(slug, slug)


def coerce_application(value) -> Application:
    slug = normalize_application_slug(value if value is not None else None)
    if slug in _APPLICATION_SLUGS:
        return slug  # type: ignore[return-value]
    return DEFAULT_APPLICATION

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
    model_config = ConfigDict(populate_by_name=True)

    study_type: str
    route: list[Route] | None = None
    route_evidence: str | None = None
    route_confidence: ConfidenceLevel | None = None
    application: Application = Field(
        default=DEFAULT_APPLICATION,
        validation_alias=AliasChoices("application", "study_domain"),
    )
    application_evidence: str | None = Field(
        default=None,
        validation_alias=AliasChoices(
            "application_evidence", "study_domain_evidence"
        ),
    )
    application_confidence: ConfidenceLevel | None = Field(
        default=None,
        validation_alias=AliasChoices(
            "application_confidence", "study_domain_confidence"
        ),
    )
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

    @field_validator("route", mode="before")
    @classmethod
    def _coerce_route(cls, value):
        return coerce_route_list(value)

    @field_validator("application", mode="before")
    @classmethod
    def _coerce_application(cls, value):
        return coerce_application(value)


class ExtractionResult(BaseModel):
    raw: RawExtraction
    endpoint_category: EndpointCategory | None = None


class ProtocolParameters(BaseModel):
    """Flattened view used by retrieval and legacy API fields."""

    model_config = ConfigDict(populate_by_name=True)

    endpoint_category: EndpointCategory | None = None
    route: list[Route] | None = None
    application: Application = Field(
        default=DEFAULT_APPLICATION,
        validation_alias=AliasChoices("application", "study_domain"),
    )
    procedure_text: str | None = None
    species: Species | None = None
    n_animals: int | None = None
    regulatory: bool | None = None

    @field_validator("route", mode="before")
    @classmethod
    def _coerce_route(cls, value):
        return coerce_route_list(value)

    @field_validator("application", mode="before")
    @classmethod
    def _coerce_application(cls, value):
        return coerce_application(value)

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
        application=result.raw.application,
        procedure_text=result.raw.procedure_text,
        species=result.raw.species,
        n_animals=primary_animal_count(result.raw.animal_counts),
        regulatory=result.raw.regulatory,
    )


class AnalyzeRequest(BaseModel):
    protocol_text: str = Field(..., min_length=20, max_length=10000)
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
    lang: Literal["pt", "en"] | None = None


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
