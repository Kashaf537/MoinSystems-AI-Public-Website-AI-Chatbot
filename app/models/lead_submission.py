import uuid
from datetime import datetime

from sqlalchemy import DateTime, ForeignKey, String, Text, func
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db.base import Base
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from app.models.chat_session import ChatSession
    from app.models.email_notification import EmailNotification


class LeadSubmission(Base):
    __tablename__ = "lead_submission"

    id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        primary_key=True,
        default=uuid.uuid4,
    )
    session_id: Mapped[uuid.UUID | None] = mapped_column(
        ForeignKey("chat_session.id", ondelete="SET NULL"),
        nullable=True,
    )
    full_name: Mapped[str] = mapped_column(String(255))
    email: Mapped[str] = mapped_column(String(255))
    contact_number: Mapped[str] = mapped_column(String(50))
    company_name: Mapped[str | None] = mapped_column(String(255), nullable=True)
    project_summary: Mapped[str | None] = mapped_column(Text, nullable=True)
    required_services: Mapped[str | None] = mapped_column(Text, nullable=True)
    timeline: Mapped[str | None] = mapped_column(String(255), nullable=True)
    budget_range: Mapped[str | None] = mapped_column(String(255), nullable=True)
    current_software: Mapped[str | None] = mapped_column(Text, nullable=True)
    integrations: Mapped[str | None] = mapped_column(Text, nullable=True)
    source_page: Mapped[str | None] = mapped_column(String(512), nullable=True)
    conversation_summary: Mapped[str | None] = mapped_column(Text, nullable=True)
    lead_status: Mapped[str] = mapped_column(String(20), default="New")
    crm_record_id: Mapped[str | None] = mapped_column(String(100), nullable=True)
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        server_default=func.now(),
    )

    session: Mapped["ChatSession"] = relationship(back_populates="leads")
    email_notifications: Mapped[list["EmailNotification"]] = relationship(
        back_populates="lead",
        cascade="all, delete-orphan",
    )
