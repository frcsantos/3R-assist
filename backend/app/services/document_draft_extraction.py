from app.adapters.llm import ExtractionError, LLMAdapter
from app.models.document_draft import DocumentDraftExtractResponse


class DocumentDraftExtractionService:
    def __init__(self, llm: LLMAdapter) -> None:
        self._llm = llm

    def extract(
        self,
        text: str,
        *,
        category_hint: str | None = None,
        source_url: str | None = None,
    ) -> DocumentDraftExtractResponse | ExtractionError:
        return self._llm.extract_document_draft(
            text,
            category_hint=category_hint,
            source_url=source_url,
        )
