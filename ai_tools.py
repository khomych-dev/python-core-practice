from typing import Any

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from models import CarDB


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
