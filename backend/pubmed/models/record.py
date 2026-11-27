from __future__ import annotations

from pydantic import BaseModel, computed_field


class Author(BaseModel):
    last_name: str | None = None
    fore_name: str | None = None
    affiliation: str | None = None

    @computed_field
    @property
    def display_name(self) -> str:
        parts = [p for p in (self.fore_name, self.last_name) if p]
        return " ".join(parts) if parts else "Unknown"


class PubMedRecord(BaseModel):
    pmid: str
    title: str
    authors: list[Author]
    institutions: list[str]
    pub_year: int | None = None
    pub_month: int | None = None
    journal: str | None = None
    abstract_text: str
    endpoint_text: str
    method_text: str
    mesh_terms: list[str]
    cluster: str
    doi: str | None = None
    source: str = "pubmed"
    published_doi: str | None = None

    def to_endpoint_embedding_text(self) -> str:
        """Title + endpoint/hypothesis context — drives Path A search."""
        return f"{self.title}. {self.endpoint_text}"

    def to_method_embedding_text(self) -> str:
        """Method description — drives Path B search."""
        return self.method_text
