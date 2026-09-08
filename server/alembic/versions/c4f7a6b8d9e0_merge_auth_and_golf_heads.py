"""merge auth and golf migration heads

Revision ID: c4f7a6b8d9e0
Revises: ae3f6b2c9e4a, b9e2a5d5f3a1
Create Date: 2026-09-04 00:00:00.000000

"""
from typing import Sequence, Union


# revision identifiers, used by Alembic.
revision: str = "c4f7a6b8d9e0"
down_revision: Union[str, Sequence[str], None] = ("ae3f6b2c9e4a", "b9e2a5d5f3a1")
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    pass


def downgrade() -> None:
    pass
