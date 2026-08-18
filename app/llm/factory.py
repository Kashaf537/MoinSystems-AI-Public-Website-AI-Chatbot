from functools import lru_cache

from app.config import get_settings
from app.llm.base import LLMProvider


@lru_cache
def get_llm_provider() -> LLMProvider:
    """
    Returns the configured provider based on LLM_PROVIDER.
    Cached per process — call get_llm_provider.cache_clear() in tests
    that need to swap providers mid-run.
    """
    settings = get_settings()

    if settings.LLM_PROVIDER == "openai":
        from app.llm.openai_provider import OpenAIProvider

        return OpenAIProvider()

    if settings.LLM_PROVIDER == "anthropic":
        from app.llm.anthropic_provider import AnthropicProvider

        return AnthropicProvider()

    raise ValueError(f"Unsupported LLM_PROVIDER: {settings.LLM_PROVIDER!r}")
