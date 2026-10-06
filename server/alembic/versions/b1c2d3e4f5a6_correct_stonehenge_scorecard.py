"""Correct Stonehenge pars and Black tee yardages.

Revision ID: b1c2d3e4f5a6
Revises: a7c8d9e0f1a2
Create Date: 2026-10-05
"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


revision: str = "b1c2d3e4f5a6"
down_revision: Union[str, Sequence[str], None] = "a7c8d9e0f1a2"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


OFFICIAL_HOLES = {
    1: (4, 424), 2: (4, 396), 3: (3, 174), 4: (4, 426),
    5: (3, 204), 6: (5, 509), 7: (3, 195), 8: (4, 441),
    9: (5, 563), 10: (4, 404), 11: (5, 549), 12: (4, 460),
    13: (3, 188), 14: (4, 406), 15: (4, 381), 16: (4, 431),
    17: (3, 197), 18: (5, 553),
}

OLD_SEED_HOLES = {
    1: (4, 390), 2: (5, 510), 3: (4, 415), 4: (3, 175),
    5: (4, 386), 6: (5, 525), 7: (4, 432), 8: (3, 168),
    9: (5, 535), 10: (4, 397), 11: (3, 158), 12: (4, 420),
    13: (5, 548), 14: (4, 401), 15: (3, 172), 16: (4, 448),
    17: (4, 413), 18: (5, 520),
}


def _update_holes(values: dict[int, tuple[int, int]]) -> None:
    connection = op.get_bind()
    for hole_number, (par, yardage) in values.items():
        connection.execute(
            sa.text(
                "UPDATE holes SET par = :par, yardage = :yardage "
                "FROM courses WHERE holes.course_id = courses.id "
                "AND courses.name = :course_name AND holes.hole_number = :hole_number"
            ),
            {
                "par": par,
                "yardage": yardage,
                "course_name": "Stonehenge Golf Course",
                "hole_number": hole_number,
            },
        )


def upgrade() -> None:
    _update_holes(OFFICIAL_HOLES)


def downgrade() -> None:
    _update_holes(OLD_SEED_HOLES)
