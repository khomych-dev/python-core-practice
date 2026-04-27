from typing import Annotated, Any

from fastapi import APIRouter, Depends, status
from pydantic import BaseModel, Field, field_validator

from auth import get_current_user, require_admin
from dependencies import get_car_service
from services.car_service import CarService

router = APIRouter(prefix="/api/v1/cars", tags=["Cars"])


class CarRegisterRequest(BaseModel):
    owner: str = Field(min_length=2)
    plate_number: str = Field(min_length=3, max_length=8)
    brand: str = Field(min_length=2)

    @field_validator("plate_number")
    @classmethod
    def format_plate(cls, value: str) -> str:
        return value.replace(" ", "").upper()


class StatusUpdateRequest(BaseModel):
    new_status: str = Field(min_length=3)


class MessageResponse(BaseModel):
    message: str


@router.get("/")
async def all_cars(
    current_user: Annotated[dict[str, Any], Depends(get_current_user)],
    service: Annotated[CarService, Depends(get_car_service)],
) -> list[dict[str, Any]]:
    cars = await service.get_all_cars()
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


@router.post("/", status_code=status.HTTP_201_CREATED, response_model=MessageResponse)
async def register_new_car(
    request: CarRegisterRequest,
    current_user: Annotated[dict[str, Any], Depends(get_current_user)],
    service: Annotated[CarService, Depends(get_car_service)],
) -> MessageResponse:

    await service.register_car(
        plate_number=request.plate_number, brand=request.brand, owner=request.owner, username=current_user["username"]
    )

    return MessageResponse(
        message=f"The vehicle {request.brand} ({request.plate_number}) has been successfully registered."
    )


@router.patch("/{plate_number}/status", response_model=MessageResponse)
async def new_status(
    plate_number: str,
    request: StatusUpdateRequest,
    admin_user: Annotated[dict[str, Any], Depends(require_admin)],
    service: Annotated[CarService, Depends(get_car_service)],
) -> MessageResponse:

    await service.update_status(
        plate_number=plate_number, new_status=request.new_status, admin_username=admin_user["username"]
    )

    return MessageResponse(
        message=f"The status for vehicle {plate_number} has been successfully changed to '{request.new_status}'."
    )


@router.delete("/{plate_number}", response_model=MessageResponse)
async def delete_car(
    plate_number: str,
    admin_user: Annotated[dict[str, Any], Depends(require_admin)],
    service: Annotated[CarService, Depends(get_car_service)],
) -> MessageResponse:

    await service.delete_car(plate_number=plate_number, admin_username=admin_user["username"])

    return MessageResponse(
        message=f"The vehicle with license plate {plate_number} "
        f"has been successfully deleted by the administrator {admin_user['username']}."
    )


@router.get("/health")
async def health_check() -> dict[str, str]:
    return {"status": "ok", "message": "CI/CD Pipeline is working perfectly!"}
