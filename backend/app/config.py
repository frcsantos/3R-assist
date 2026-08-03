from functools import lru_cache
from pathlib import Path

from pydantic import Field
from pydantic_settings import BaseSettings, SettingsConfigDict

_BACKEND_DIR = Path(__file__).resolve().parents[1]
_PROJECT_ROOT = _BACKEND_DIR.parent


class Settings(BaseSettings):
    model_config = SettingsConfigDict(
        env_file=(
            str(_PROJECT_ROOT / ".env"),
            str(_BACKEND_DIR / ".env"),
        ),
        env_file_encoding="utf-8",
        extra="ignore",
    )

    app_env: str = Field(default="development", alias="APP_ENV")
    app_base_url: str = Field(default="http://localhost:5173", alias="APP_BASE_URL")
    cors_origins: str = Field(
        default="http://localhost:5173",
        alias="CORS_ORIGINS",
    )

    database_url: str = Field(
        default="",
        alias="DATABASE_URL",
    )

    anthropic_api_key: str | None = Field(default=None, alias="ANTHROPIC_API_KEY")
    openrouter_api_key: str | None = Field(default=None, alias="OPENROUTER_API_KEY")
    openai_api_key: str | None = Field(default=None, alias="OPENAI_API_KEY")
    llm_model: str | None = Field(default=None, alias="LLM_MODEL")
    anthropic_model: str = Field(
        default="claude-sonnet-4-20250514",
        alias="ANTHROPIC_MODEL",
    )

    ollama_model: str | None = Field(default=None, alias="OLLAMA_MODEL")

    embedding_model: str = Field(
        default="all-MiniLM-L6-v2",
        alias="EMBEDDING_MODEL",
    )

    semantic_ranking: bool = Field(
        default=False,
        alias="SEMANTIC_RANKING",
    )

    auth_secret: str | None = Field(default=None, alias="AUTH_SECRET")

    @property
    def cors_origin_list(self) -> list[str]:
        return [origin.strip() for origin in self.cors_origins.split(",") if origin.strip()]

    @property
    def resolved_llm_model(self) -> str:
        model = self.llm_model or self.anthropic_model
        if model.startswith("openrouter/"):
            return model
        if self.openrouter_api_key:
            if model.startswith("openai/") and not self.openai_api_key:
                return f"openrouter/{model}"
            if model.startswith("anthropic/") and not self.anthropic_api_key:
                return f"openrouter/{model}"
            if not model.startswith(
                ("anthropic/", "openai/", "gemini/", "xai/")
            ):
                return f"openrouter/{model}"
        if "/" not in model:
            return f"anthropic/{model}"
        return model

    @property
    def use_stub_llm(self) -> bool:
        return not any(
            (
                self.anthropic_api_key,
                self.openrouter_api_key,
                self.openai_api_key,
            )
        )


@lru_cache
def get_settings() -> Settings:
    return Settings()
