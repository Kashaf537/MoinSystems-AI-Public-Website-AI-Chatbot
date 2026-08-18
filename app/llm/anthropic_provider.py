import anthropic

from app.config import get_settings
from app.llm.base import ChatMessageIn, LLMProvider, LLMResponse

DEFAULT_MODEL = "claude-sonnet-4-6"


class AnthropicProvider(LLMProvider):
    name = "anthropic"

    def __init__(self, model: str = DEFAULT_MODEL) -> None:
        settings = get_settings()
        if not settings.ANTHROPIC_API_KEY:
            raise RuntimeError("ANTHROPIC_API_KEY is not set")
        self._client = anthropic.Anthropic(api_key=settings.ANTHROPIC_API_KEY)
        self._model = model

    def generate(
        self, messages: list[ChatMessageIn], *, max_tokens: int = 1000
    ) -> LLMResponse:
        # Anthropic takes the system prompt separately from the message list.
        system_prompt = "\n".join(m.content for m in messages if m.role == "system")
        turn_messages = [
            {"role": m.role, "content": m.content}
            for m in messages
            if m.role != "system"
        ]

        response = self._client.messages.create(
            model=self._model,
            max_tokens=max_tokens,
            system=system_prompt or None,
            messages=turn_messages,
        )
        text = "".join(block.text for block in response.content if block.type == "text")
        return LLMResponse(content=text, provider=self.name, model=self._model)
