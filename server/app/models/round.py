from datetime import date

from sqlalchemy import Boolean, Date, ForeignKey
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db.base import Base


class Round(Base):
    __tablename__ = "rounds"

    id: Mapped[int] = mapped_column(primary_key=True)

    user_id: Mapped[int] = mapped_column(
        ForeignKey("users.id"),
        nullable=False
    )

    course_id: Mapped[int] = mapped_column(
        ForeignKey("courses.id"),
        nullable=False
    )

    date: Mapped[date] = mapped_column(
        Date,
        nullable=False
    )

    score: Mapped[int | None] = mapped_column(
        nullable=True
    )

    is_complete: Mapped[bool] = mapped_column(
        Boolean,
        nullable=False,
        default=False,
        server_default="false",
    )

    user: Mapped["User"] = relationship(
        back_populates="rounds"
    )

    course: Mapped["Course"] = relationship(
        back_populates="rounds"
    )

    shots: Mapped[list["Shot"]] = relationship(
        back_populates="round",
        cascade="all, delete-orphan"
    )

    # per-hole scores for this round
    scores: Mapped[list["RoundScore"]] = relationship(
        back_populates="round",
        cascade="all, delete-orphan"
    )
