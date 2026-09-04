from sqlalchemy import ForeignKey, String
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db.base import Base


class Club(Base):
    __tablename__ = "clubs"

    id: Mapped[int] = mapped_column(primary_key=True)

    user_id: Mapped[int] = mapped_column(
        ForeignKey("users.id"),
        nullable=False
    )

    name: Mapped[str] = mapped_column(
        String(50),
        nullable=False
    )

    carry_distance: Mapped[float | None] = mapped_column(
        nullable=True
    )

    total_distance: Mapped[float | None] = mapped_column(
        nullable=True
    )

    user: Mapped["User"] = relationship(
        back_populates="clubs"
    )

    shots: Mapped[list["Shot"]] = relationship(
        back_populates="club"
    )
