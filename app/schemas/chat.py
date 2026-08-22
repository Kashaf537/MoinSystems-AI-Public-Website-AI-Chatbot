"""
Day 4 - Chat API request and response schemas.
"""

from pydantic import BaseModel, Field


class ChatMessage(BaseModel):
    """Single conversation message."""

    role: str = Field(
        ...,
        pattern="^(user|assistant)$",
    )

    content: str = Field(
        ...,
        min_length=1,
        max_length=10000,
    )


class ChatRequest(BaseModel):
    """Request body for the chat endpoint."""

    message: str = Field(
        ...,
        min_length=1,
        max_length=10000,
    )

    history: list[ChatMessage] = Field(
        default_factory=list,
        max_length=20,
    )

    intent: str | None = Field(
        default=None,
        max_length=100,
    )

    lead_state: str | None = Field(
        default=None,
        max_length=100,
    )


class ChatResponse(BaseModel):
    """Structured chat response."""

    response: str

    provider: str

    model: str