from abc import ABC, abstractmethod
from dataclasses import dataclass


@dataclass
class ChatMessageIn:
    role: str
    content: str


@dataclass
class LLMResponse:
    content: str
    provider: str
    model: str
    raw: dict | None = None


class LLMProvider(ABC):
    name: str

    @abstractmethod
    def generate(
        self, messages: list[ChatMessageIn], *, max_tokens: int = 1000
    ) -> LLMResponse:
        raise NotImplementedError
