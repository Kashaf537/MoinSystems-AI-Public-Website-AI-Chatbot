import uuid
from datetime import datetime

from sqlalchemy import DateTime, String, Text, func
from sqlalchemy.dialects.postgresql import JSONB, UUID
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db.base import Base

from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from app.models.knowledge_chunk import KnowledgeChunk


class KnowledgeDocument(Base):
    __tablename__ = "knowledge_document"

    id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        primary_key=True,
        default=uuid.uuid4,
    )
    external_id: Mapped[str] = mapped_column(
        String(100),
        unique=True,
        nullable=False,
    )
    title: Mapped[str] = mapped_column(String(512))
    category: Mapped[str] = mapped_column(String(100))
    tags: Mapped[str | None] = mapped_column(Text, nullable=True)
    intents: Mapped[str | None] = mapped_column(Text, nullable=True)
    content: Mapped[str] = mapped_column(Text)
    data_status: Mapped[str] = mapped_column(
        String(50),
        default="cleaned_validated",
    )
    source_basis: Mapped[str | None] = mapped_column(
        String(100),
        nullable=True,
    )
    dataset_version: Mapped[str] = mapped_column(String(50))
    metadata_json: Mapped[dict | None] = mapped_column(
        JSONB,
        nullable=True,
    )
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        server_default=func.now(),
    )

    chunks: Mapped[list["KnowledgeChunk"]] = relationship(
        back_populates="document",
        cascade="all, delete-orphan",
    )
