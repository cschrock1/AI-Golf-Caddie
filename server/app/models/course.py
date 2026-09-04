from sqlalchemy import String
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db.base import Base


class Course(Base):
    __tablename__ = "courses"

    id: Mapped[int] = mapped_column(primary_key=True)

    name: Mapped[str] = mapped_column(
        String(150),
        nullable=False
    )

    city: Mapped[str | None] = mapped_column(
        String(100),
        nullable=True
    )

    state: Mapped[str | None] = mapped_column(
        String(50),
        nullable=True
    )

    holes: Mapped[list["Hole"]] = relationship(
        back_populates="course",
        cascade="all, delete-orphan"
    )

    rounds: Mapped[list["Round"]] = relationship(
        back_populates="course"
    )
