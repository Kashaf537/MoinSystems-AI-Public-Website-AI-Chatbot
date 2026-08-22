import uuid

from pydantic import BaseModel, Field


class SessionCreateRequest(BaseModel):
    source_page: str | None = Field(
        default=None,
        max_length=512,
    )


class SessionCreateResponse(BaseModel):
    session_id: uuid.UUID
    lead_state: str