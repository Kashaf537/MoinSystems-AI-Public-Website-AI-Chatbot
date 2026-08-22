"""
Day 4 - LLM provider abstraction.

Defines the common interface used by all LLM providers.
"""

from abc import ABC, abstractmethod
from dataclasses import dataclass


@dataclass
class LLMResponse:
    """Normalized response returned by every LLM provider."""

    content: str
    model: str
    provider: str


class LLMProvider(ABC):
    """Abstract interface for LLM providers."""

    @abstractmethod
    def generate(
        self,
        system_prompt: str,
        messages: list[dict[str, str]],
    ) -> LLMResponse:
        """
        Generate a response using the configured provider.
        """
        raise NotImplementedError