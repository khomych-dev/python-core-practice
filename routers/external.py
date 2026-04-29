from typing import Annotated

from fastapi import APIRouter, Depends, HTTPException, status

from dependencies import get_car_service, verify_api_key
from models import ApiKeyDB
from services.car_service import CarService

router = APIRouter(prefix="/api/v1/external", tags=["External B2B API"])


@router.get("/cars/{plate_number}/status")
async def get_car_status(
    plate_number: str,
    api_key: Annotated[ApiKeyDB, Depends(verify_api_key)],
    car_service: Annotated[CarService, Depends(get_car_service)],
) -> dict[str, str]:

    car = await car_service.repo.get_by_plate(plate_number)

    if not car:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Vehicle with license plate {plate_number} was not found in our garage.",
        )

    return {
        "plate_number": car.plate_number,
        "status": car.status,
        "partner": api_key.owner_name,
        "message": "Authorized via B2B API Key",
    }
