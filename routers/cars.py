from fastapi import APIRouter, status, HTTPException, Depends, Request
from pydantic import BaseModel, Field, field_validator
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from logger import log

from models import CarDB
from auth import get_current_user, require_admin, get_db

router = APIRouter(prefix="/api/v1/cars")


class CarRegisterRequest(BaseModel):
    owner: str = Field(min_length=2)
    plate_number: str = Field(min_length=3, max_length=8)
    brand: str = Field(min_length=2)

    @field_validator("plate_number")
    @classmethod
    def format_plate(cls, value: str) -> str:
        cleaned = value.replace(" ", "").upper()

        return cleaned


class StatusUpdateRequest(BaseModel):
    new_status: str = Field(min_length=3)


class MessageResponse(BaseModel):
    message: str


@router.get("/")
async def all_cars(
    current_user: dict = Depends(get_current_user), db: AsyncSession = Depends(get_db)
):
    stmt = select(CarDB)
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


@router.post("/", status_code=status.HTTP_201_CREATED, response_model=MessageResponse)
async def register_new_car(
    request: CarRegisterRequest,
    current_user: dict = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    username = current_user["username"]
    log.info(
        "car_registration_started",
        username=username,
        plate_number=request.plate_number,
        action_type="audit",
    )

    stmt = select(CarDB).where(CarDB.plate_number == request.plate_number)
    result = await db.execute(stmt)
    if result.scalar_one_or_none():
        raise HTTPException(
            status_code=400,
            detail=f"Car with plate {request.plate_number} is already in the database.",
        )

    new_car = CarDB(
        plate_number=request.plate_number,
        brand=request.brand,
        owner=request.owner,
        status="in_garage",
        mechanic_username=username,
    )

    db.add(new_car)
    await db.commit()

    return {
        "message": f"Vehicle {request.brand} ({request.plate_number}) successfully registered by {username}."
    }


@router.patch("/{plate_number}/status", response_model=MessageResponse)
async def new_status(
    plate_number: str,
    request: StatusUpdateRequest,
    admin_user: dict = Depends(require_admin),
    db: AsyncSession = Depends(get_db),
):
    username = admin_user["username"]

    log.info(
        "car_status_updated",
        username=username,
        plate_number=plate_number,
        new_status=request.new_status,
        action_type="audit",
    )

    stmt = select(CarDB).where(CarDB.plate_number == plate_number)
    result = await db.execute(stmt)
    car = result.scalar_one_or_none()

    if not car:
        raise HTTPException(
            status_code=404, detail=f"Car with plate {plate_number} not found"
        )

    car.status = request.new_status

    await db.commit()

    return {
        "message": f"Status for car {plate_number} successfully updated to '{request.new_status}'"
    }


@router.delete("/{plate_number}", response_model=MessageResponse)
async def delete_car(
    plate_number: str,
    admin_user: dict = Depends(require_admin),
    db: AsyncSession = Depends(get_db),
):
    admin_name = admin_user["username"]
    log.warning(
        "car_deleted",
        admin_username=admin_name,
        plate_number=plate_number,
        action_type="audit",
    )

    stmt = select(CarDB).where(CarDB.plate_number == plate_number)
    result = await db.execute(stmt)
    car = result.scalar_one_or_none()

    if not car:
        raise HTTPException(
            status_code=404, detail=f"Car with plate {plate_number} not found"
        )

    if car.status != "released":
        raise HTTPException(
            status_code=400,
            detail=f"Cannot delete car. Current status is '{car.status}'. Change status to 'released' first.",
        )

    await db.delete(car)
    await db.commit()

    return {
        "message": f"The car {plate_number} has been successfully deleted by the administrator {admin_name}."
    }


@router.post("/test-email", response_model=MessageResponse)
async def test_background_email(email: str, request: Request):
    redis = request.app.state.redis

    await redis.enqueue_job(
        "send_notification_task", email, "Your car is ready! Please pay 5,000 UAH."
    )

    return {
        "message": f"Request received! An email will be sent to {email} in the background."
    }


@router.get("/health")
async def health_check():
    return {"status": "ok", "message": "CI/CD Pipeline is working perfectly!"}
