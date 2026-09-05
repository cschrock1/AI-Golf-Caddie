"""add geospatial hole geometries

Revision ID: e1a2b3c4d5e6
Revises: d8e9f0a1b2c3
Create Date: 2026-09-04 00:00:00.000000

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa
from geoalchemy2 import Geometry


revision: str = "e1a2b3c4d5e6"
down_revision: Union[str, Sequence[str], None] = "d8e9f0a1b2c3"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.execute("CREATE EXTENSION IF NOT EXISTS postgis")

    op.add_column("holes", sa.Column("tee_location", Geometry("POINT", srid=4326)))
    op.add_column("holes", sa.Column("pin_location", Geometry("POINT", srid=4326)))
    op.add_column("holes", sa.Column("green_geometry", Geometry("POLYGON", srid=4326)))
    op.add_column("holes", sa.Column("fairway_geometry", Geometry("POLYGON", srid=4326)))
    op.add_column("holes", sa.Column("bunker_geometry", Geometry("MULTIPOLYGON", srid=4326)))
    op.add_column("holes", sa.Column("water_geometry", Geometry("MULTIPOLYGON", srid=4326)))


def downgrade() -> None:
    for column in (
        "water_geometry",
        "bunker_geometry",
        "fairway_geometry",
        "green_geometry",
        "pin_location",
        "tee_location",
    ):
        op.drop_column("holes", column)