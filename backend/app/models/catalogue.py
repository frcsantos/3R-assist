from pydantic import BaseModel, Field

from app.models.document import Document
from app.models.method import Method, MethodRegulatoryContext


class MethodCatalogueItem(BaseModel):
    method: Method
    regulatory_contexts: list[MethodRegulatoryContext] = Field(default_factory=list)


class MethodsCatalogueResponse(BaseModel):
    methods: list[MethodCatalogueItem] = Field(default_factory=list)


class DocumentsCatalogueResponse(BaseModel):
    documents: list[Document] = Field(default_factory=list)
