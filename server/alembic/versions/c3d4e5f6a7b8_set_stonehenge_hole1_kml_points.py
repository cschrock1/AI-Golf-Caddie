"""Set Stonehenge Hole 1 tee and green centers from the KML.

Revision ID: c3d4e5f6a7b8
Revises: b1c2d3e4f5a6
Create Date: 2026-10-05
"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


revision: str = "c3d4e5f6a7b8"
down_revision: Union[str, Sequence[str], None] = "b1c2d3e4f5a6"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.get_bind().execute(sa.text(
        "UPDATE holes SET "
        "tee_location = ST_SetSRID(ST_MakePoint(-85.78491237783246, 41.2053717585335), 4326), "
        "pin_location = ST_SetSRID(ST_MakePoint(-85.78498208763907, 41.20273912570412), 4326) "
        "FROM courses WHERE holes.course_id = courses.id "
        "AND lower(courses.name) LIKE '%stonehenge%' "
        "AND holes.hole_number = 1"
    ))


def downgrade() -> None:
    # These are corrections to imported source coordinates; there is no reliable
    # prior value to restore, so leave the corrected KML points in place.
    pass
