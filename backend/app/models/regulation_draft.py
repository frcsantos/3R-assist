from typing import Literal
import json

from pydantic import BaseModel, Field, field_validator, model_validator

from app.models.i18n import LocalizedStr, localized_str, parse_localized_str
from app.models.method import RegulatoryStatus
from app.models.policy import looks_like_single_url


class RegulationDraftExtractRequest(BaseModel):
    text: str = Field(..., min_length=1, max_length=50000)
    source_url: str | None = Field(default=None, max_length=2000)
    lang: Literal["pt", "en"] | None = None

    @field_validator("text")
    @classmethod
    def strip_text(cls, value: str) -> str:
        return value.strip()

    @model_validator(mode="after")
    def require_length_unless_url(self) -> "RegulationDraftExtractRequest":
        if looks_like_single_url(self.text):
            return self
        if len(self.text) < 20:
            raise ValueError("text must be at least 20 characters unless it is a URL")
        return self


class RegulationDraftFields(BaseModel):
    jurisdiction: LocalizedStr | None = None
    regulatory_status: RegulatoryStatus | None = None
    regulatory_date: str | None = None
    regulatory_endpoints: list[int] | None = None
    endpoint_quote: str | None = None
    regulatory_body: LocalizedStr | None = None
    regulatory_citation: LocalizedStr | None = None
    notes: str | None = None

    @field_validator("regulatory_endpoints", mode="before")
    @classmethod
    def _coerce_endpoint_ids(cls, value):
        if value is None:
            return None
        if isinstance(value, str) and not value.strip():
            return None
        if isinstance(value, str):
            parsed = value.strip()
            if parsed.startswith("["):
                value = json.loads(parsed)
            else:
                return None
        if isinstance(value, (tuple, list)):
            ids: list[int] = []
            for item in value:
                try:
                    ids.append(int(item))
                except (TypeError, ValueError):
                    continue
            return ids or None
        return None

    @field_validator(
        "regulatory_body",
        "regulatory_citation",
        mode="before",
    )
    @classmethod
    def _coerce_localized(cls, value):
        if value is None:
            return None
        if isinstance(value, str) and not value.strip():
            return None
        if isinstance(value, str) and not value.strip().startswith("{"):
            return localized_str(value)
        parsed = parse_localized_str(value, required=False)
        if parsed is None:
            return None
        if not parsed.en_us.strip() and not parsed.pt_br.strip():
            return None
        return parsed


class RegulationDraftExtractResponse(BaseModel):
    fields: RegulationDraftFields
