import uuid
from datetime import datetime

from sqlalchemy import (
    DateTime,
    ForeignKey,
    Integer,
    String,
    Text,
    func,
)
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db.base import Base

from typing import TYPE_CHECKING


if TYPE_CHECKING:
    from app.models.lead_submission import LeadSubmission


class EmailNotification(Base):

    __tablename__ = "email_notification"

    # =========================================================
    # Primary Key
    # =========================================================

    id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        primary_key=True,
        default=uuid.uuid4,
    )

    # =========================================================
    # Lead
    # =========================================================

    lead_id: Mapped[uuid.UUID] = mapped_column(
        ForeignKey(
            "lead_submission.id",
            ondelete="CASCADE",
        ),
        nullable=False,
    )

    # =========================================================
    # Email Information
    # =========================================================

    recipient: Mapped[str] = mapped_column(
        String(255),
        default="info@moinsystemsai.com",
        nullable=False,
    )

    status: Mapped[str] = mapped_column(
        String(20),
        default="pending",
        nullable=False,
    )

    provider: Mapped[str | None] = mapped_column(
        String(50),
        nullable=True,
    )

    provider_message_id: Mapped[str | None] = mapped_column(
        String(255),
        nullable=True,
    )

    # =========================================================
    # Error / Retry Information
    # =========================================================

    error_detail: Mapped[str | None] = mapped_column(
        Text,
        nullable=True,
    )

    retry_count: Mapped[int] = mapped_column(
        Integer,
        default=0,
        nullable=False,
    )

    # =========================================================
    # Timestamps
    # =========================================================

    attempted_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        server_default=func.now(),
        nullable=False,
    )

    sent_at: Mapped[datetime | None] = mapped_column(
        DateTime(timezone=True),
        nullable=True,
    )

    # =========================================================
    # Relationship
    # =========================================================

    lead: Mapped["LeadSubmission"] = relationship(
        back_populates="email_notifications",
    )

