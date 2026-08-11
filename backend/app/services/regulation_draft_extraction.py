from app.adapters.llm import ExtractionError, LLMAdapter
from app.models.regulation_draft import RegulationDraftExtractResponse


class RegulationDraftExtractionService:
    def __init__(self, llm: LLMAdapter) -> None:
        self._llm = llm

    def extract(
        self,
        text: str,
        *,
        source_url: str | None = None,
    ) -> RegulationDraftExtractResponse | ExtractionError:
        return self._llm.extract_regulation_draft(text, source_url=source_url)
