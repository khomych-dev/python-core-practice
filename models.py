import secrets
from datetime import UTC, datetime
from typing import Any

from sqlalchemy import Boolean, DateTime, ForeignKey, String, text
from sqlalchemy.dialects.postgresql import JSONB
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column, relationship


class Base(DeclarativeBase):
    pass


class CarDB(Base):
    __tablename__ = "cars"

    plate_number: Mapped[str] = mapped_column(String, primary_key=True)
    brand: Mapped[str] = mapped_column(String, index=True)
    status: Mapped[str] = mapped_column(String)
    owner: Mapped[str | None] = mapped_column(String, nullable=True)
    mechanic_username: Mapped[str] = mapped_column(ForeignKey("users.username"))
    mechanic: Mapped["UserDB"] = relationship(back_populates="cars")


class UserDB(Base):
    __tablename__ = "users"

    username: Mapped[str] = mapped_column(String, primary_key=True)
    hashed_password: Mapped[str] = mapped_column(String)
    role: Mapped[str] = mapped_column(String, default="mechanic")
    cars: Mapped[list["CarDB"]] = relationship(back_populates="mechanic")


class RepairHistoryDB(Base):
    __tablename__ = "repair_history"

    id: Mapped[int] = mapped_column(primary_key=True, index=True)
    car_plate_number: Mapped[str] = mapped_column(ForeignKey("cars.plate_number", ondelete="CASCADE"), index=True)
    mechanic_username: Mapped[str] = mapped_column(ForeignKey("users.username", ondelete="SET NULL"), nullable=True)
    raw_text: Mapped[str] = mapped_column(nullable=False)
    ai_summary: Mapped[dict[str, Any]] = mapped_column(JSONB, nullable=False)
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), default=lambda: datetime.now(UTC), server_default=text("TIMEZONE('utc', now())")
    )


class ApiKeyDB(Base):
    __tablename__ = "api_keys"

    id: Mapped[int] = mapped_column(primary_key=True, index=True)
    key: Mapped[str] = mapped_column(String, unique=True, index=True, default=lambda: secrets.token_urlsafe(32))
    owner_name: Mapped[str] = mapped_column(String, nullable=False)
    is_active: Mapped[bool] = mapped_column(Boolean, default=True)
