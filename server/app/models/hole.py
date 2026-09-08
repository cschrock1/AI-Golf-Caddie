from sqlalchemy import ForeignKey
from sqlalchemy.orm import Mapped, mapped_column, relationship
from geoalchemy2 import Geometry

from app.db.base import Base


class Hole(Base):
    __tablename__ = "holes"

    id: Mapped[int] = mapped_column(primary_key=True)

    course_id: Mapped[int] = mapped_column(
        ForeignKey("courses.id"),
        nullable=False
    )

    hole_number: Mapped[int] = mapped_column(
        nullable=False
    )

    par: Mapped[int] = mapped_column(
        nullable=False
    )

    yardage: Mapped[int] = mapped_column(
        nullable=False
    )

    tee_location = mapped_column(
        Geometry("POINT", srid=4326, spatial_index=True),
        nullable=True
    )

    pin_location = mapped_column(
        Geometry("POINT", srid=4326, spatial_index=True),
        nullable=True
    )

    green_geometry = mapped_column(
        Geometry("POLYGON", srid=4326, spatial_index=True),
        nullable=True
    )

    fairway_geometry = mapped_column(
        Geometry("POLYGON", srid=4326, spatial_index=True),
        nullable=True
    )

    bunker_geometry = mapped_column(
        Geometry("MULTIPOLYGON", srid=4326, spatial_index=True),
        nullable=True
    )

    water_geometry = mapped_column(
        Geometry("MULTIPOLYGON", srid=4326, spatial_index=True),
        nullable=True
    )

    course: Mapped["Course"] = relationship(
        back_populates="holes"
    )

    shots: Mapped[list["Shot"]] = relationship(
        back_populates="hole"
    )
