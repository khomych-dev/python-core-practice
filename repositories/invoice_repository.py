from collections.abc import Sequence

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from models import InvoiceDB


class InvoiceRepository:
    def __init__(self, session: AsyncSession):
        self.session = session

    async def add(self, invoice: InvoiceDB) -> InvoiceDB:
        self.session.add(invoice)
        await self.session.commit()
        await self.session.refresh(invoice)
        return invoice

    async def get_by_plate(self, plate_number: str) -> Sequence[InvoiceDB]:
        stmt = select(InvoiceDB).where(InvoiceDB.car_plate_number == plate_number)
        result = await self.session.execute(stmt)
        return result.scalars().all()

    async def get_by_stripe_id(self, stripe_id: str) -> InvoiceDB | None:
        stmt = select(InvoiceDB).where(InvoiceDB.stripe_payment_intent_id == stripe_id)
        result = await self.session.execute(stmt)
        return result.scalar_one_or_none()

    async def commit(self) -> None:
        await self.session.commit()
