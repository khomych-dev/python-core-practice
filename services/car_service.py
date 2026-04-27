from collections.abc import Sequence
from typing import Any

from fastapi import HTTPException

from logger import log
from models import CarDB
from repositories.car_repository import CarRepository


class CarService:
    def __init__(self, repo: CarRepository, redis_pool: Any):
        self.repo = repo
        self.redis_pool = redis_pool

    async def get_all_cars(self) -> Sequence[CarDB]:
        return await self.repo.get_all()

    async def register_car(self, plate_number: str, brand: str, owner: str, username: str) -> CarDB:
        existing_car = await self.repo.get_by_plate(plate_number)
        if existing_car:
            raise HTTPException(
                status_code=400, detail=f"The vehicle with license plate {plate_number} is already in the database."
            )

        new_car = CarDB(
            plate_number=plate_number,
            brand=brand,
            owner=owner,
            status="in_garage",
            mechanic_username=username,
        )

        log.info(
            "car_registration_started",
            username=username,
            plate_number=plate_number,
            action_type="audit",
        )

        return await self.repo.add(new_car)

    async def update_status(self, plate_number: str, new_status: str, admin_username: str) -> None:
        car = await self.repo.get_by_plate(plate_number)
        if not car:
            raise HTTPException(status_code=404, detail=f"The vehicle with license plate {plate_number} was not found.")

        car.status = new_status
        await self.repo.commit()

        log.info(
            "car_status_updated",
            username=admin_username,
            plate_number=plate_number,
            new_status=new_status,
            action_type="audit",
        )

        if new_status == "released":
            await self.redis_pool.enqueue_job("generate_invoice_task", plate_number)

    async def delete_car(self, plate_number: str, admin_username: str) -> None:
        car = await self.repo.get_by_plate(plate_number)
        if not car:
            raise HTTPException(status_code=404, detail=f"The vehicle with license plate {plate_number} was not found.")

        if car.status != "released":
            raise HTTPException(
                status_code=400,
                detail=f"The car cannot be deleted. The current status is '{car.status}'. "
                "First, change the status to 'released'.",
            )

        log.warning(
            "car_deleted",
            admin_username=admin_username,
            plate_number=plate_number,
            action_type="audit",
        )

        await self.repo.delete(car)

    async def get_cars_by_status(self, status: str) -> Sequence[CarDB]:
        return await self.repo.get_by_status(status)
