"""Shared types for extraction reliability ground truth."""

from dataclasses import dataclass, field


@dataclass(frozen=True)
class ExpectedSplitting:
    """How many experiments the model should return for a protocol."""

    min_count: int = 1
    max_count: int | None = 1
    primary_index: int = 0


@dataclass(frozen=True)
class ExpectedAnimalCounts:
    female: int | None = None
    male: int | None = None
    total: int | None = None
    per_group: int | None = None


@dataclass(frozen=True)
class ExpectedEvidence:
    """Minimal substring anchors for LLM evidence fields (ADR-016).

    Each value is a short phrase from the source text (no filler). A test passes when
    the model's evidence excerpt contains it, case-insensitively. Use a tuple when
    any one of several minimal anchors is acceptable.
    """

    route: str | tuple[str, ...] | None = None
    application: str | tuple[str, ...] | None = None
    procedure_text: str | tuple[str, ...] | None = None
    species: str | tuple[str, ...] | None = None
    animal_counts: str | tuple[str, ...] | None = None
    regulatory: str | tuple[str, ...] | None = None


@dataclass(frozen=True)
class ExpectedExtraction:
    study_type_keywords: tuple[str, ...]
    endpoint_category: str | None
    route: list[str] | None
    application: set[str]  # any listed value is acceptable
    procedure_keywords: tuple[str, ...]
    species: str | None
    animal_counts: ExpectedAnimalCounts | None
    regulatory: bool | None
    evidence: ExpectedEvidence | None = None
    notes: str | None = None
