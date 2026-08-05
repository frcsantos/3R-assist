from datetime import date as Date

from pydantic import BaseModel

from app.models.i18n import LocalizedStr


class Document(BaseModel):
    id: int
    slug: str
    doc_citation: LocalizedStr
    date: Date | None = None
    category: str
    url: str | None = None
