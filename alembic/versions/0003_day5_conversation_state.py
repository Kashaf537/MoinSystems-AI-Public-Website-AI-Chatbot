"""Day 5 conversation state and message metadata.

Revision ID: 0003
Revises: 0002
"""

from typing import Sequence, Union

import sqlalchemy as sa
from alembic import op


revision: str = "0003"

down_revision: Union[str, None] = "0002"

branch_labels: Union[str, Sequence[str], None] = None

depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:

    # ---------------------------------------------------------
    # Session state
    # ---------------------------------------------------------

    op.add_column(
        "chat_session",
        sa.Column(
            "current_intent",
            sa.String(50),
            nullable=True,
        ),
    )

    op.add_column(
        "chat_session",
        sa.Column(
            "lead_state",
            sa.String(50),
            nullable=False,
            server_default="NONE",
        ),
    )

    op.add_column(
        "chat_session",
        sa.Column(
            "lead_data",
            sa.JSON(),
            nullable=True,
        ),
    )

    # ---------------------------------------------------------
    # Message metadata
    # ---------------------------------------------------------

    op.add_column(
        "chat_message",
        sa.Column(
            "intent",
            sa.String(50),
            nullable=True,
        ),
    )

    op.add_column(
        "chat_message",
        sa.Column(
            "lead_state",
            sa.String(50),
            nullable=True,
        ),
    )


def downgrade() -> None:

    op.drop_column(
        "chat_message",
        "lead_state",
    )

    op.drop_column(
        "chat_message",
        "intent",
    )

    op.drop_column(
        "chat_session",
        "lead_data",
    )

    op.drop_column(
        "chat_session",
        "lead_state",
    )

    op.drop_column(
        "chat_session",
        "current_intent",
    )