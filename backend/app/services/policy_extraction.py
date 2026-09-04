from app.adapters.llm import ExtractionError, LLMAdapter
from app.models.policy import PolicyExtractResponse
from app.services.language import detect_lang, language_label


class PolicyExtractionService:
    def __init__(self, llm: LLMAdapter) -> None:
        self._llm = llm

    def extract(
        self,
        text: str,
        *,
        source_url: str | None = None,
    ) -> PolicyExtractResponse | ExtractionError:
        lang = detect_lang(text)
        result = self._llm.extract_policy(
            text,
            source_url=source_url,
            source_language=language_label(lang),
        )
        if isinstance(result, ExtractionError):
            return result
        return result.model_copy(update={"lang": lang})
