from fastapi import APIRouter, status, HTTPException, Depends
from pydantic import BaseModel, Field
import logging
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select

from models import CarDB
from auth import get_current_user, require_admin, get_db

router = APIRouter(prefix="/api/v1/cars")
logger = logging.getLogger(__name__)


class CarRegisterRequest(BaseModel):
    owner: str = Field(min_length=2)
    plate_number: str = Field(min_length=3, max_length=8)
    brand: str = Field(min_length=2)


class StatusUpdateRequest(BaseModel):
    new_status: str = Field(min_length=3)


class MessageResponse(BaseModel):
    message: str


@router.get("/")
async def all_cars(
    current_user: dict = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    stmt = select(CarDB)
    result = await db.execute(stmt)
    cars = result.scalars().all()

    return [
        {
            "plate_number": car.plate_number,
            "brand": car.brand,
            "owner": car.owner,
            "status": car.status
        }
        for car in cars
    ]


@router.post("/", status_code=status.HTTP_201_CREATED, response_model=MessageResponse)
async def register_new_car(
    request: CarRegisterRequest,
    current_user: dict = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    username = current_user["username"]
    logger.info(
        f"[AUDIT] User '{username}' is registering the vehicle {request.plate_number}")

    stmt = select(CarDB).where(CarDB.plate_number == request.plate_number)
    result = await db.execute(stmt)
    if result.scalar_one_or_none():
        raise HTTPException(
            status_code=400, detail=f"Car with plate {request.plate_number} is already in the database.")

    new_car = CarDB(
        plate_number=request.plate_number,
        brand=request.brand,
        owner=request.owner,
        status="in_garage"
    )

    db.add(new_car)
    await db.commit()

    return {"message": f"Vehicle {request.brand} ({request.plate_number}) successfully registered by {username}."}


@router.patch("/{plate_number}/status", response_model=MessageResponse)
async def new_status(
    plate_number: str,
    request: StatusUpdateRequest,
    current_user: dict = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    username = current_user["username"]

    logger.info(
        f"[AUDIT] User '{username}' changed status of car {plate_number} to '{request.new_status}'")

    stmt = select(CarDB).where(CarDB.plate_number == plate_number)
    result = await db.execute(stmt)
    car = result.scalar_one_or_none()

    if not car:
        raise HTTPException(
            status_code=404, detail=f"Car with plate {plate_number} not found")

    car.status = request.new_status

    await db.commit()

    return {"message": f"Status for car {plate_number} successfully updated to '{request.new_status}'"}


@router.delete("/{plate_number}", response_model=MessageResponse)
async def delete_car(
    plate_number: str,
    admin_user: dict = Depends(require_admin),
    db: AsyncSession = Depends(get_db)
):
    admin_name = admin_user["username"]
    logger.warning(
        f"[AUDIT] ADMINISTRATOR '{admin_name}' IS DELETING CAR {plate_number}")

    stmt = select(CarDB).where(CarDB.plate_number == plate_number)
    result = await db.execute(stmt)
    car = result.scalar_one_or_none()

    if not car:
        raise HTTPException(
            status_code=404, detail=f"Car with plate {plate_number} not found")

    await db.delete(car)
    await db.commit()

    return {"message": f"The car {plate_number} has been successfully deleted by the administrator {admin_name}."}
