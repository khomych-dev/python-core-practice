from typing import Any

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from models import CarDB, RepairHistoryDB


async def get_cars_in_garage(db: AsyncSession, status: str | None = None) -> list[dict[str, Any]]:
    """
    Retrieves a list of cars from the database.
    Optionally filters by the car's status (e.g., 'in_garage', 'released').
    """
    stmt = select(CarDB)

    if status:
        stmt = stmt.where(CarDB.status == status)

    result = await db.execute(stmt)
    cars = result.scalars().all()

    return [
        {
            "plate_number": car.plate_number,
            "brand": car.brand,
            "owner": car.owner,
            "status": car.status,
            "mechanic": car.mechanic_username,
        }
        for car in cars
    ]


async def get_repair_history(db: AsyncSession, plate_number: str) -> list[dict[str, Any]]:
    """
    Retrieves the full repair history for a specific car by its plate number.
    Use this when the user asks what was fixed, what parts were used, or about the history of a car.
    """
    stmt = select(RepairHistoryDB).where(RepairHistoryDB.car_plate_number == plate_number)
    result = await db.execute(stmt)
    records = result.scalars().all()

    return [
        {
            "mechanic": record.mechanic_username,
            "text": record.raw_text,
            "date": record.created_at.isoformat() if record.created_at else None,
        }
        for record in records
    ]
