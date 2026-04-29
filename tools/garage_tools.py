from typing import Any

from pydantic import BaseModel, Field

from services.car_service import CarService
from services.repair_service import RepairService
from tools.core import BaseTool


class GetCarsArgs(BaseModel):
    status: str | None = Field(default=None, description="Filter by 'in_garage' or 'released'.")
    plate_number: str | None = Field(default=None, description="Filter by plate number, e.g., BC7777CB")


class GetCarsTool(BaseTool):
    name = "get_cars"
    description = "Get car details (owner, brand, status)."
    args_schema = GetCarsArgs

    def __init__(self, car_service: CarService) -> None:
        self.car_service = car_service

    async def execute(self, **kwargs: Any) -> list[dict[str, Any]]:
        status = kwargs.get("status")
        plate_number = kwargs.get("plate_number")

        if plate_number:
            car = await self.car_service.repo.get_by_plate(plate_number)
            cars = [car] if car else []
        elif status:
            cars_seq = await self.car_service.get_cars_by_status(status)
            cars = list(cars_seq)
        else:
            cars_seq = await self.car_service.get_all_cars()
            cars = list(cars_seq)

        if not cars:
            return [{"error": "No cars found matching the criteria"}]

        return [
            {
                "plate_number": c.plate_number,
                "brand": c.brand,
                "owner": c.owner,
                "status": c.status,
                "mechanic": c.mechanic_username,
            }
            for c in cars
        ]


class GetRepairHistoryArgs(BaseModel):
    plate_number: str = Field(description="Plate number, e.g., BC7777CB")


class GetRepairHistoryTool(BaseTool):
    name = "get_repair_history"
    description = "Get detailed repair history for a specific car."
    args_schema = GetRepairHistoryArgs

    def __init__(self, repair_service: RepairService) -> None:
        self.repair_service = repair_service

    async def execute(self, **kwargs: Any) -> list[dict[str, Any]]:
        plate_number = str(kwargs["plate_number"])
        history = await self.repair_service.repo.get_by_car_plate(plate_number)

        if not history:
            return [{"message": "No history found"}]

        return [
            {
                "mechanic": h.mechanic_username,
                "text": h.raw_text,
                "date": h.created_at.isoformat() if h.created_at else None,
            }
            for h in history
        ]
