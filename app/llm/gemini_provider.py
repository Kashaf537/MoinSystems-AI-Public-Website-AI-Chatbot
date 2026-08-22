"""
Day 4 - Gemini LLM provider.

Uses Google's Gemini API through its OpenAI-compatible endpoint.
This keeps the LLM provider abstraction independent from the
chat orchestration layer.
"""

from openai import OpenAI

from app.core.config import get_settings
from app.llm.base import LLMProvider, LLMResponse


class GeminiProvider(LLMProvider):
    """Google Gemini implementation of the LLM provider interface."""

    GEMINI_BASE_URL = (
        "https://generativelanguage.googleapis.com/v1beta/openai/"
    )

    def __init__(self) -> None:
        self.settings = get_settings()

        if not self.settings.GEMINI_API_KEY:
            raise ValueError(
                "GEMINI_API_KEY is not configured."
            )

        self.client = OpenAI(
            api_key=self.settings.GEMINI_API_KEY,
            base_url=self.GEMINI_BASE_URL,
        )

    def generate(
        self,
        system_prompt: str,
        messages: list[dict[str, str]],
    ) -> LLMResponse:

        response = self.client.chat.completions.create(
            model=self.settings.LLM_MODEL,
            temperature=self.settings.LLM_TEMPERATURE,
            max_tokens=self.settings.LLM_MAX_TOKENS,
            messages=[
                {
                    "role": "system",
                    "content": system_prompt,
                },
                *messages,
            ],
        )

        content = response.choices[0].message.content

        if not content:
            raise RuntimeError(
                "Gemini returned an empty response."
            )

        return LLMResponse(
            content=content.strip(),
            model=self.settings.LLM_MODEL,
            provider="gemini",
        )