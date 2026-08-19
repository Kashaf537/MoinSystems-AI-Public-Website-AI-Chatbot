"""change knowledge embeddings to 384 dimensions

Revision ID: 0002
Revises: 0001
Create Date: 2026-08-19
"""

from typing import Sequence, Union

import sqlalchemy as sa
from alembic import op
from pgvector.sqlalchemy import Vector


revision: str = "0002"
down_revision: Union[str, None] = "0001"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # Remove the old vector index before changing the column type.
    op.drop_index(
        "ix_knowledge_chunk_embedding",
        table_name="knowledge_chunk",
    )

    # Change embedding dimension from 1536 to 384.
    op.alter_column(
        "knowledge_chunk",
        "embedding",
        existing_type=Vector(1536),
        type_=Vector(384),
        existing_nullable=True,
        postgresql_using="embedding::vector(384)",
    )

    # Recreate the cosine similarity index.
    op.execute(
        """
        CREATE INDEX ix_knowledge_chunk_embedding
        ON knowledge_chunk
        USING ivfflat (embedding vector_cosine_ops)
        WITH (lists = 100)
        """
    )


def downgrade() -> None:
    # Remove 384-dimensional index.
    op.drop_index(
        "ix_knowledge_chunk_embedding",
        table_name="knowledge_chunk",
    )

    # Change back to 1536 dimensions.
    op.alter_column(
        "knowledge_chunk",
        "embedding",
        existing_type=Vector(384),
        type_=Vector(1536),
        existing_nullable=True,
        postgresql_using="embedding::vector(1536)",
    )

    # Recreate the old index.
    op.execute(
        """
        CREATE INDEX ix_knowledge_chunk_embedding
        ON knowledge_chunk
        USING ivfflat (embedding vector_cosine_ops)
        WITH (lists = 100)
        """
    )