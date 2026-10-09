"""Keep one score per round and hole.

Revision ID: d4e5f6a7b8c9
Revises: c3d4e5f6a7b8
Create Date: 2026-10-08
"""
from typing import Sequence, Union

from alembic import op


revision: str = "d4e5f6a7b8c9"
down_revision: Union[str, Sequence[str], None] = "c3d4e5f6a7b8"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # Preserve the most recently inserted record if earlier autosaves raced.
    op.execute(
        """
        DELETE FROM round_scores
        WHERE id IN (
            SELECT id
            FROM (
                SELECT id,
                       row_number() OVER (
                           PARTITION BY round_id, hole_id
                           ORDER BY id DESC
                       ) AS duplicate_rank
                FROM round_scores
            ) ranked_scores
            WHERE duplicate_rank > 1
        )
        """
    )
    op.create_unique_constraint(
        "uq_round_scores_round_hole",
        "round_scores",
        ["round_id", "hole_id"],
    )


def downgrade() -> None:
    op.drop_constraint(
        "uq_round_scores_round_hole",
        "round_scores",
        type_="unique",
    )
