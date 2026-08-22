import uuid

from pydantic import BaseModel, Field


class LeadCaptureRequest(BaseModel):

    session_id: uuid.UUID

    full_name: str | None = Field(
        default=None,
        max_length=255,
    )

    email: str | None = Field(
        default=None,
        max_length=255,
    )

    contact_number: str | None = Field(
        default=None,
        max_length=50,
    )

    company_name: str | None = Field(
        default=None,
        max_length=255,
    )

    project_summary: str | None = None

    required_services: str | None = None

    timeline: str | None = Field(
        default=None,
        max_length=255,
    )

    budget_range: str | None = Field(
        default=None,
        max_length=255,
    )

    source_page: str | None = Field(
        default=None,
        max_length=512,
    )


class LeadCaptureResponse(BaseModel):

    success: bool

    lead_id: uuid.UUID | None = None

    lead_state: str

    message: str