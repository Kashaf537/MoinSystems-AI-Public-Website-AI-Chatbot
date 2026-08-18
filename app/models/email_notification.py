import uuid
from datetime import datetime

from sqlalchemy import DateTime, ForeignKey, String, Text, func
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db.base import Base
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from app.models.lead_submission import LeadSubmission


class EmailNotification(Base):
    __tablename__ = "email_notification"

    id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        primary_key=True,
        default=uuid.uuid4,
    )
    lead_id: Mapped[uuid.UUID] = mapped_column(
        ForeignKey("lead_submission.id", ondelete="CASCADE")
    )
    recipient: Mapped[str] = mapped_column(
        String(255),
        default="info@moinsystemsai.com",
    )
    status: Mapped[str] = mapped_column(
        String(20),
        default="pending",
    )
    provider: Mapped[str | None] = mapped_column(String(50), nullable=True)
    error_detail: Mapped[str | None] = mapped_column(Text, nullable=True)
    attempted_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        server_default=func.now(),
    )
    sent_at: Mapped[datetime | None] = mapped_column(
        DateTime(timezone=True),
        nullable=True,
    )

    lead: Mapped["LeadSubmission"] = relationship(back_populates="email_notifications")
