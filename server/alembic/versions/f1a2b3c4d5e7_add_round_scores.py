"""add round_scores table

Revision ID: f1a2b3c4d5e7
Revises: b9e2a5d5f3a1
Create Date: 2026-09-17 00:00:00.000000

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = 'f1a2b3c4d5e7'
down_revision: Union[str, Sequence[str], None] = 'b9e2a5d5f3a1'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.create_table(
        'round_scores',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('round_id', sa.Integer(), nullable=False),
        sa.Column('hole_id', sa.Integer(), nullable=False),
        sa.Column('strokes', sa.Integer(), nullable=False),
        sa.ForeignKeyConstraint(['hole_id'], ['holes.id']),
        sa.ForeignKeyConstraint(['round_id'], ['rounds.id']),
        sa.PrimaryKeyConstraint('id')
    )


def downgrade() -> None:
    op.drop_table('round_scores')
