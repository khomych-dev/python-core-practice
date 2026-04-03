from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column
from sqlalchemy import String


class Base(DeclarativeBase):
    pass


class CarDB(Base):
    __tablename__ = "cars"

    plate_number: Mapped[str] = mapped_column(String, primary_key=True)
    brand: Mapped[str] = mapped_column(String)
    status: Mapped[str] = mapped_column(String)
    owner: Mapped[str | None] = mapped_column(String, nullable=True)


class UserDB(Base):
    __tablename__ = "users"

    username: Mapped[str] = mapped_column(String, primary_key=True)
    hashed_password: Mapped[str] = mapped_column(String)
    role: Mapped[str] = mapped_column(String, default="mechanic")
