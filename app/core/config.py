from functools import lru_cache

from pydantic_settings import (
    BaseSettings,
    SettingsConfigDict,
)


class Settings(BaseSettings):

    APP_NAME: str = (
        "MoinSystems AI Public Website AI Chatbot"
    )

    APP_ENV: str = "local"

    DEBUG: bool = True

    DATABASE_URL: str

    # =========================================================
    # LLM Providers
    # =========================================================

    GEMINI_API_KEY: str | None = None
    LLM_PROVIDER: str = "gemini"
    LLM_MODEL: str = "gemini-2.5-flash"

    LLM_TEMPERATURE: float = 0.2

    LLM_MAX_TOKENS: int = 500

    # =========================================================
    #              Email / SMTP
    # =========================================================
    SMTP_HOST: str = "smtp.gmail.com"
    SMTP_PORT: int = 587
    SMTP_USERNAME: str
    SMTP_PASSWORD: str
    EMAIL_FROM: str
    EMAIL_TO: str = "info@moinsystemsai.com"
    EMAIL_TIMEOUT: int = 15

    # =========================================================
    # Embeddings
    # =========================================================

    EMBEDDING_MODEL: str = (
        "sentence-transformers/all-MiniLM-L6-v2"
    )

    # =========================================================
    # RAG
    # =========================================================

    RAG_TOP_K: int = 5

    RAG_SCORE_THRESHOLD: float = 0.35

    RAG_MAX_CONTEXT_RESULTS: int = 5

    RAG_MAX_HISTORY_MESSAGES: int = 6

    # =========================================================
    # CORS
    # =========================================================

    ALLOWED_ORIGINS: str = (
        "http://localhost:3000"
    )

    @property
    def allowed_origins_list(self) -> list[str]:
        return [
            origin.strip()
            for origin in self.ALLOWED_ORIGINS.split(",")
            if origin.strip()
        ]

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        extra="ignore",
    )


@lru_cache
def get_settings() -> Settings:
    return Settings()