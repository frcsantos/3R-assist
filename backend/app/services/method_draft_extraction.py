from app.adapters.llm import ExtractionError, LLMAdapter
from app.models.method_draft import MethodDraftExtractResponse


class MethodDraftExtractionService:
    def __init__(self, llm: LLMAdapter) -> None:
        self._llm = llm

    def extract(self, text: str) -> MethodDraftExtractResponse | ExtractionError:
        return self._llm.extract_method_draft(text)
