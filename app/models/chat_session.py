import uuid
from datetime import datetime
from typing import TYPE_CHECKING

from sqlalchemy import JSON, DateTime, String, func
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db.base import Base


if TYPE_CHECKING:
    from app.models.chat_message import ChatMessage
    from app.models.lead_submission import LeadSubmission


class ChatSession(Base):

    __tablename__ = "chat_session"

    # =========================================================
    # Primary Key
    # =========================================================

    id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        primary_key=True,
        default=uuid.uuid4,
    )

    # =========================================================
    # Session Information
    # =========================================================

    source_page: Mapped[str | None] = mapped_column(
        String(512),
        nullable=True,
    )

    # =========================================================
    # Day 5 - Conversation State
    # =========================================================

    current_intent: Mapped[str | None] = mapped_column(
        String(50),
        nullable=True,
    )

    lead_state: Mapped[str] = mapped_column(
        String(50),
        default="NONE",
        nullable=False,
    )

    lead_data: Mapped[dict | None] = mapped_column(
        JSON,
        nullable=True,
    )

    # =========================================================
    # Timestamps
    # =========================================================

    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        server_default=func.now(),
    )

    last_active_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        server_default=func.now(),
        onupdate=func.now(),
    )

    # =========================================================
    # Relationships
    # =========================================================

    messages: Mapped[list["ChatMessage"]] = relationship(
        back_populates="session",
        cascade="all, delete-orphan",
    )

    leads: Mapped[list["LeadSubmission"]] = relationship(
        back_populates="session",
    )