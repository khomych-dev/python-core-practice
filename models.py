from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column, relationship
from sqlalchemy import String, ForeignKey


class Base(DeclarativeBase):
    pass


class CarDB(Base):
    __tablename__ = "cars"

    plate_number: Mapped[str] = mapped_column(String, primary_key=True)
    brand: Mapped[str] = mapped_column(String)
    status: Mapped[str] = mapped_column(String)
    owner: Mapped[str | None] = mapped_column(String, nullable=True)
    mechanic_username: Mapped[str] = mapped_column(
        ForeignKey("users.username"))
    mechanic: Mapped["UserDB"] = relationship(back_populates="cars")


class UserDB(Base):
    __tablename__ = "users"

    username: Mapped[str] = mapped_column(String, primary_key=True)
    hashed_password: Mapped[str] = mapped_column(String)
    role: Mapped[str] = mapped_column(String, default="mechanic")
    cars: Mapped[list["CarDB"]] = relationship(back_populates="mechanic")
