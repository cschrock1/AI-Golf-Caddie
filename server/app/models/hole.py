from sqlalchemy import ForeignKey
from sqlalchemy.orm import Mapped, mapped_column, relationship

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

    course: Mapped["Course"] = relationship(
        back_populates="holes"
    )

    shots: Mapped[list["Shot"]] = relationship(
        back_populates="hole"
    )
