from app.adapters.llm import ExtractionError, LLMAdapter
from app.models.policy import PolicyExtractResponse


class PolicyExtractionService:
    def __init__(self, llm: LLMAdapter) -> None:
        self._llm = llm

    def extract(
        self,
        text: str,
        *,
        source_url: str | None = None,
    ) -> PolicyExtractResponse | ExtractionError:
        return self._llm.extract_policy(text, source_url=source_url)
