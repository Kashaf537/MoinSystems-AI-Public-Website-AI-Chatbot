import uuid

from pydantic import BaseModel, Field


class HistoryMessage(BaseModel):

    role: str

    content: str


class ChatRequest(BaseModel):

    session_id: uuid.UUID

    message: str = Field(
        min_length=1,
        max_length=4000,
    )

    history: list[HistoryMessage] = Field(
        default_factory=list,
        max_length=6,
    )

    intent: str | None = None

    lead_state: str | None = None


class ChatResponse(BaseModel):

    response: str

    provider: str

    model: str

    session_id: uuid.UUID

    intent: str

    lead_state: str

    lead_capture_required: bool = False