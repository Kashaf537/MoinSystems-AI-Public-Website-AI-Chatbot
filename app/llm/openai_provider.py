from openai import OpenAI

from app.config import get_settings
from app.llm.base import ChatMessageIn, LLMProvider, LLMResponse

DEFAULT_MODEL = "gpt-4o-mini"


class OpenAIProvider(LLMProvider):
    name = "openai"

    def __init__(self, model: str = DEFAULT_MODEL) -> None:
        settings = get_settings()
        if not settings.OPENAI_API_KEY:
            raise RuntimeError("OPENAI_API_KEY is not set")
        self._client = OpenAI(api_key=settings.OPENAI_API_KEY)
        self._model = model

    def generate(
        self, messages: list[ChatMessageIn], *, max_tokens: int = 1000
    ) -> LLMResponse:
        response = self._client.chat.completions.create(
            model=self._model,
            max_tokens=max_tokens,
            messages=[{"role": m.role, "content": m.content} for m in messages],
        )
        return LLMResponse(
            content=response.choices[0].message.content or "",
            provider=self.name,
            model=self._model,
        )
