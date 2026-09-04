from sqlalchemy import ForeignKey, String
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db.base import Base


class Shot(Base):
    __tablename__ = "shots"

    id: Mapped[int] = mapped_column(primary_key=True)

    round_id: Mapped[int] = mapped_column(
        ForeignKey("rounds.id"),
        nullable=False
    )

    hole_id: Mapped[int] = mapped_column(
        ForeignKey("holes.id"),
        nullable=False
    )

    club_id: Mapped[int] = mapped_column(
        ForeignKey("clubs.id"),
        nullable=False
    )

    start_distance: Mapped[float | None] = mapped_column(
        nullable=True
    )

    end_distance: Mapped[float | None] = mapped_column(
        nullable=True
    )

    result: Mapped[str | None] = mapped_column(
        String(100),
        nullable=True
    )

    round: Mapped["Round"] = relationship(
        back_populates="shots"
    )

    hole: Mapped["Hole"] = relationship(
        back_populates="shots"
    )

    club: Mapped["Club"] = relationship(
        back_populates="shots"
    )
