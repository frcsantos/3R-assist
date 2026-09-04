from datetime import date as Date

from pydantic import BaseModel, Field

from app.models.i18n import LocalizedStr


class Document(BaseModel):
    id: int
    slug: str
    doc_citation: LocalizedStr
    description: LocalizedStr | None = None
    date: Date | None = None
    categories: list[str] = Field(default_factory=list)
    institution: LocalizedStr | None = None
    url: str | None = None
