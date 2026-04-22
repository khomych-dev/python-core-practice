from sqlalchemy.ext.asyncio import AsyncSession

from models import RepairHistoryDB
from schemas import RepairHistoryCreate


async def save_history_to_db(db: AsyncSession, repair_data: RepairHistoryCreate) -> RepairHistoryDB:
    new_history = RepairHistoryDB(**repair_data.model_dump())

    db.add(new_history)
    await db.commit()
    await db.refresh(new_history)

    return new_history
