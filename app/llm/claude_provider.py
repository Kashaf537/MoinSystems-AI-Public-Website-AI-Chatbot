"""
Day 4 - Anthropic Claude LLM provider.
"""

from anthropic import Anthropic

from app.core.config import get_settings
from app.llm.base import LLMProvider, LLMResponse


class ClaudeProvider(LLMProvider):
    """Anthropic Claude implementation."""

    def __init__(self) -> None:
        self.settings = get_settings()

        if not self.settings.ANTHROPIC_API_KEY:
            raise ValueError(
                "ANTHROPIC_API_KEY is not configured."
            )

        self.client = Anthropic(
            api_key=self.settings.ANTHROPIC_API_KEY
        )

    def generate(
        self,
        system_prompt: str,
        messages: list[dict[str, str]],
    ) -> LLMResponse:

        response = self.client.messages.create(
            model=self.settings.LLM_MODEL,
            system=system_prompt,
            messages=messages,
            temperature=self.settings.LLM_TEMPERATURE,
            max_tokens=self.settings.LLM_MAX_TOKENS,
        )

        text_parts = []

        for block in response.content:
            if getattr(block, "type", None) == "text":
                text_parts.append(block.text)

        content = "\n".join(text_parts).strip()

        if not content:
            raise RuntimeError(
                "Claude returned an empty response."
            )

        return LLMResponse(
            content=content,
            model=self.settings.LLM_MODEL,
            provider="claude",
        )