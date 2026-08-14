from app.adapters.llm import ExtractionError, LLMAdapter
from app.models.document_draft import DocumentDraftExtractResponse
from app.services.language import detect_lang, language_label


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
        lang = detect_lang(text)
        result = self._llm.extract_document_draft(
            text,
            category_hint=category_hint,
            source_url=source_url,
            source_language=language_label(lang),
        )
        if isinstance(result, ExtractionError):
            return result
        return result.model_copy(update={"lang": lang})
