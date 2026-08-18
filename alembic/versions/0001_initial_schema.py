"""initial schema: chat_session, chat_message, lead_submission,
email_notification, knowledge_document, knowledge_chunk

Revision ID: 0001
Revises:
Create Date: 2026-08-18

"""

from typing import Sequence, Union

import sqlalchemy as sa
from alembic import op
from pgvector.sqlalchemy import Vector
from sqlalchemy.dialects.postgresql import JSONB, UUID

revision: str = "0001"
down_revision: Union[str, None] = None
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None

EMBEDDING_DIM = 1536


def upgrade() -> None:
    op.execute("CREATE EXTENSION IF NOT EXISTS vector")

    op.create_table(
        "chat_session",
        sa.Column("id", UUID(as_uuid=True), primary_key=True),
        sa.Column("source_page", sa.String(512), nullable=True),
        sa.Column(
            "created_at", sa.DateTime(timezone=True), server_default=sa.func.now()
        ),
        sa.Column(
            "last_active_at", sa.DateTime(timezone=True), server_default=sa.func.now()
        ),
    )

    op.create_table(
        "chat_message",
        sa.Column("id", UUID(as_uuid=True), primary_key=True),
        sa.Column(
            "session_id",
            UUID(as_uuid=True),
            sa.ForeignKey("chat_session.id", ondelete="CASCADE"),
            nullable=False,
        ),
        sa.Column("role", sa.String(20), nullable=False),
        sa.Column("content", sa.Text, nullable=False),
        sa.Column(
            "created_at", sa.DateTime(timezone=True), server_default=sa.func.now()
        ),
    )
    op.create_index("ix_chat_message_session_id", "chat_message", ["session_id"])

    op.create_table(
        "lead_submission",
        sa.Column("id", UUID(as_uuid=True), primary_key=True),
        sa.Column(
            "session_id",
            UUID(as_uuid=True),
            sa.ForeignKey("chat_session.id", ondelete="SET NULL"),
            nullable=True,
        ),
        sa.Column("full_name", sa.String(255), nullable=False),
        sa.Column("email", sa.String(255), nullable=False),
        sa.Column("contact_number", sa.String(50), nullable=False),
        sa.Column("company_name", sa.String(255), nullable=True),
        sa.Column("project_summary", sa.Text, nullable=True),
        sa.Column("required_services", sa.Text, nullable=True),
        sa.Column("timeline", sa.String(255), nullable=True),
        sa.Column("budget_range", sa.String(255), nullable=True),
        sa.Column("current_software", sa.Text, nullable=True),
        sa.Column("integrations", sa.Text, nullable=True),
        sa.Column("source_page", sa.String(512), nullable=True),
        sa.Column("conversation_summary", sa.Text, nullable=True),
        sa.Column("lead_status", sa.String(20), server_default="New"),
        sa.Column("crm_record_id", sa.String(100), nullable=True),
        sa.Column(
            "created_at", sa.DateTime(timezone=True), server_default=sa.func.now()
        ),
    )

    op.create_table(
        "email_notification",
        sa.Column("id", UUID(as_uuid=True), primary_key=True),
        sa.Column(
            "lead_id",
            UUID(as_uuid=True),
            sa.ForeignKey("lead_submission.id", ondelete="CASCADE"),
            nullable=False,
        ),
        sa.Column("recipient", sa.String(255), server_default="info@moinsystemsai.com"),
        sa.Column("status", sa.String(20), server_default="pending"),
        sa.Column("provider", sa.String(50), nullable=True),
        sa.Column("error_detail", sa.Text, nullable=True),
        sa.Column(
            "attempted_at", sa.DateTime(timezone=True), server_default=sa.func.now()
        ),
        sa.Column("sent_at", sa.DateTime(timezone=True), nullable=True),
    )
    op.create_index("ix_email_notification_lead_id", "email_notification", ["lead_id"])

    op.create_table(
        "knowledge_document",
        sa.Column("id", UUID(as_uuid=True), primary_key=True),
        sa.Column("external_id", sa.String(100), nullable=False, unique=True),
        sa.Column("title", sa.String(512), nullable=False),
        sa.Column("category", sa.String(100), nullable=False),
        sa.Column("tags", sa.Text, nullable=True),
        sa.Column("intents", sa.Text, nullable=True),
        sa.Column("content", sa.Text, nullable=False),
        sa.Column("data_status", sa.String(50), server_default="cleaned_validated"),
        sa.Column("source_basis", sa.String(100), nullable=True),
        sa.Column("dataset_version", sa.String(50), nullable=False),
        sa.Column("metadata_json", JSONB, nullable=True),
        sa.Column(
            "created_at", sa.DateTime(timezone=True), server_default=sa.func.now()
        ),
    )
    op.create_index(
        "ix_knowledge_document_category", "knowledge_document", ["category"]
    )

    op.create_table(
        "knowledge_chunk",
        sa.Column("id", UUID(as_uuid=True), primary_key=True),
        sa.Column(
            "document_id",
            UUID(as_uuid=True),
            sa.ForeignKey("knowledge_document.id", ondelete="CASCADE"),
            nullable=False,
        ),
        sa.Column("chunk_index", sa.Integer, server_default="0"),
        sa.Column("text", sa.Text, nullable=False),
        sa.Column("embedding", Vector(EMBEDDING_DIM), nullable=True),
        sa.Column(
            "created_at", sa.DateTime(timezone=True), server_default=sa.func.now()
        ),
    )
    op.create_index(
        "ix_knowledge_chunk_document_id", "knowledge_chunk", ["document_id"]
    )
    # IVFFlat index for cosine similarity search; built once rows exist (Day 2).
    op.execute(
        "CREATE INDEX ix_knowledge_chunk_embedding ON knowledge_chunk "
        "USING ivfflat (embedding vector_cosine_ops) WITH (lists = 100)"
    )


def downgrade() -> None:
    op.drop_index("ix_knowledge_chunk_embedding", table_name="knowledge_chunk")
    op.drop_table("knowledge_chunk")
    op.drop_table("knowledge_document")
    op.drop_table("email_notification")
    op.drop_table("lead_submission")
    op.drop_table("chat_message")
    op.drop_table("chat_session")
