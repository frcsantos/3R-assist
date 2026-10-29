from __future__ import annotations

from typing import Annotated, Literal

from pydantic import (
    BaseModel,
    BeforeValidator,
    ConfigDict,
    Field,
    field_validator,
)

from app.models.recommendation import Recommendation
from app.services import vocabulary
from app.services.vocabulary import DEFAULT_APPLICATION

ConfidenceLevel = Literal["high", "medium", "low"]

# Valid slugs come from the `endpoints` table (app.services.vocabulary). The
# extraction still writes the legacy underscore form (acute_toxicity), which
# normalize_endpoint_slug maps to the table slug; the value is kept as given.


def _check_endpoint_category(value):
    if value is None or not isinstance(value, str):
        return value
    # Before the table is loaded (tests, database unavailable) any value passes.
    if vocabulary.slugs_loaded("endpoints"):
        slug = normalize_endpoint_slug(value)
        if slug not in vocabulary.endpoint_slugs():
            raise ValueError(f"unknown endpoint category: {value!r}")
    return value


def normalize_endpoint_slug(value: str | None) -> str | None:
    if value is None:
        return None
    text = str(value).strip()
    if not text:
        return None
    slug = text.replace("_", "-")
    return _ENDPOINT_SLUG_ALIASES.get(slug, slug)


EndpointCategory = Annotated[str, BeforeValidator(_check_endpoint_category)]

_ENDPOINT_SLUG_ALIASES = {
    "acute-toxicity": "acute-systemic-toxicity",
    "ocular-irritation": "eye-irritation",
    "skin-absorption": "dermal-absorption",
    "bacterial-endotoxin": "bacterial-endotoxins",
    "toxicokinetics": "toxicokinetic-properties",
}

# Valid slugs come from the `routes` table (app.services.vocabulary).
Route = str


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
        if not slug or slug in routes:
            continue
        # Unknown slugs are dropped once the table is loaded; before that
        # (tests, database unavailable) any well-formed slug is kept.
        if not vocabulary.slugs_loaded("routes") or slug in vocabulary.route_slugs():
            routes.append(slug)
    return routes or None

# Valid slugs come from the `applications` table (app.services.vocabulary).
Application = str

def normalize_application_slug(value: str | None) -> str | None:
    if value is None:
        return None
    text = str(value).strip()
    if not text:
        return None
    slug = text.replace("_", "-")
    return slug


def coerce_application(value) -> Application:
    slug = normalize_application_slug(value if value is not None else None)
    if not slug:
        return DEFAULT_APPLICATION
    # Validate against the table when it has been loaded; before that (tests,
    # database unavailable) any well-formed slug is accepted as is.
    if vocabulary.applications_loaded() and slug not in vocabulary.application_slugs():
        return DEFAULT_APPLICATION
    return slug

def _check_species(value):
    if value is None or not isinstance(value, str):
        return value
    if vocabulary.slugs_loaded("species") and value not in vocabulary.species_slugs():
        raise ValueError(f"unknown species: {value!r}")
    return value


# Valid slugs come from the `species` table plus the markers in
# vocabulary.SPECIES_MARKERS (in_vitro, other).
Species = Annotated[str, BeforeValidator(_check_species)]


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
    application: Application = DEFAULT_APPLICATION
    application_evidence: str | None = None
    application_confidence: ConfidenceLevel | None = None
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
    application: Application = DEFAULT_APPLICATION
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
