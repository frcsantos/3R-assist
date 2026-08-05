from app.adapters.llm import ExtractionError, LLMAdapter
from app.models.policy import PolicyExtractResponse


class PolicyExtractionService:
    def __init__(self, llm: LLMAdapter) -> None:
        self._llm = llm

    def extract(self, text: str) -> PolicyExtractResponse | ExtractionError:
        return self._llm.extract_policy(text)
