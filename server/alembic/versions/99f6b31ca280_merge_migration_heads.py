"""merge migration heads

Revision ID: 99f6b31ca280
Revises: e1a2b3c4d5e6, f1a2b3c4d5e7
Create Date: 2026-09-29 01:49:53.826501

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '99f6b31ca280'
down_revision: Union[str, Sequence[str], None] = ('e1a2b3c4d5e6', 'f1a2b3c4d5e7')
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Upgrade schema."""
    pass


def downgrade() -> None:
    """Downgrade schema."""
    pass
