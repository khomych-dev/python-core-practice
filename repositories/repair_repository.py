from collections.abc import Sequence

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from models import RepairHistoryDB


class RepairRepository:
    def __init__(self, session: AsyncSession):
        self.session = session

    async def add(self, repair: RepairHistoryDB) -> RepairHistoryDB:
        self.session.add(repair)
        await self.session.commit()
        await self.session.refresh(repair)
        return repair

    async def get_by_car_plate(self, plate_number: str) -> Sequence[RepairHistoryDB]:
        """Отримати всю історію ремонтів для конкретного авто"""
        stmt = select(RepairHistoryDB).where(RepairHistoryDB.car_plate_number == plate_number)
        result = await self.session.execute(stmt)
        return result.scalars().all()

    async def get_by_id(self, repair_id: int) -> RepairHistoryDB | None:
        return await self.session.get(RepairHistoryDB, repair_id)
