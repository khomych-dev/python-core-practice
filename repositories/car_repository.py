from collections.abc import Sequence

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from models import CarDB


class CarRepository:
    def __init__(self, session: AsyncSession):
        """
        The repository accepts the database session upon creation.
        This allows us to easily swap out the database during testing.
        """
        self.session = session

    async def get_all(self) -> Sequence[CarDB]:
        stmt = select(CarDB)
        result = await self.session.execute(stmt)
        return result.scalars().all()

    async def get_by_plate(self, plate_number: str) -> CarDB | None:
        stmt = select(CarDB).where(CarDB.plate_number == plate_number)
        result = await self.session.execute(stmt)
        return result.scalar_one_or_none()

    async def add(self, car: CarDB) -> CarDB:
        self.session.add(car)
        await self.session.commit()
        await self.session.refresh(car)
        return car

    async def delete(self, car: CarDB) -> None:
        await self.session.delete(car)
        await self.session.commit()

    async def commit(self) -> None:
        """
        A method for saving changes if we have simply updated an object's attributes
        (for example, changed the car's status).
        """
        await self.session.commit()
