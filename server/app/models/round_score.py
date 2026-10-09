from sqlalchemy import ForeignKey, UniqueConstraint
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db.base import Base


class RoundScore(Base):
    __tablename__ = "round_scores"
    __table_args__ = (
        UniqueConstraint("round_id", "hole_id", name="uq_round_scores_round_hole"),
    )

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
