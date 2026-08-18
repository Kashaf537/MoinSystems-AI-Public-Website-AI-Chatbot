from functools import lru_cache

from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    APP_NAME: str = "# MoinSystems AI Public Website AI Chatbot"
    APP_ENV: str = "local"
    DEBUG: bool = True

    DATABASE_URL: str

    OPENAI_API_KEY: str | None = None
    ANTHROPIC_API_KEY: str | None = None

    EMBEDDING_MODEL: str = "text-embedding-3-small"

    ALLOWED_ORIGINS: str = "http://localhost:3000"

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
