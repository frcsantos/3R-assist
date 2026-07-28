from datetime import date as Date

from pydantic import BaseModel


class Document(BaseModel):
    id: int
    slug: str
    doc_ref: str
    date: Date | None = None
    category: str
    url: str | None = None
