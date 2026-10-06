"""Add round completion state.

Revision ID: a7c8d9e0f1a2
Revises: 99f6b31ca280
Create Date: 2026-10-05
"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


revision: str = "a7c8d9e0f1a2"
down_revision: Union[str, Sequence[str], None] = "99f6b31ca280"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.add_column(
        "rounds",
        sa.Column("is_complete", sa.Boolean(), server_default=sa.text("true"), nullable=False),
    )
    # Existing rounds predate the active/complete distinction and are treated as history.
    op.alter_column("rounds", "is_complete", server_default=sa.text("false"))


def downgrade() -> None:
    op.drop_column("rounds", "is_complete")
