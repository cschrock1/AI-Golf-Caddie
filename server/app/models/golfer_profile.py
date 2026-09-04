from sqlalchemy import ForeignKey
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db.base import Base


class GolferProfile(Base):
    __tablename__ = "golfer_profiles"

    id: Mapped[int] = mapped_column(primary_key=True)

    user_id: Mapped[int] = mapped_column(
        ForeignKey("users.id"),
        unique=True,
        nullable=False
    )

    handicap: Mapped[float | None] = mapped_column(nullable=True)

    preferred_tee: Mapped[str | None] = mapped_column(
        nullable=True
    )

    user: Mapped["User"] = relationship(
        back_populates="golfer_profile"
    )