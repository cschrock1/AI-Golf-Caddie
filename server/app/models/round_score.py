from sqlalchemy import ForeignKey
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db.base import Base


class RoundScore(Base):
    __tablename__ = "round_scores"

    id: Mapped[int] = mapped_column(primary_key=True)

    round_id: Mapped[int] = mapped_column(
        ForeignKey("rounds.id"),
        nullable=False
    )

    hole_id: Mapped[int] = mapped_column(
        ForeignKey("holes.id"),
        nullable=False
    )

    strokes: Mapped[int] = mapped_column(
        nullable=False
    )

    round: Mapped["Round"] = relationship(
        back_populates="scores"
    )

    hole: Mapped["Hole"] = relationship(
        back_populates="scores"
    )
