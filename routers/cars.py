from fastapi import APIRouter, status, Depends
from pydantic import BaseModel, Field
import logging

from oop_garage import Garage
from auth import get_current_user

router = APIRouter(prefix="/api/v1/cars")
my_garage = Garage()
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
async def all_cars():
    cars_dict = await my_garage.get_all_cars()
    return cars_dict


@router.post("/", status_code=status.HTTP_201_CREATED, response_model=MessageResponse)
async def register_new_car(
    request: CarRegisterRequest,
    current_user: str = Depends(get_current_user)
):
    logger.info(f"[AUDIT] User '{current_user}' is registering the vehicle {request.plate_number}")
    
    result_message = await my_garage.register_car(request.owner, request.plate_number, request.brand)
    
    return {"message": result_message}


@router.delete("/{plate_number}", response_model=MessageResponse)
async def release_car_endpoint(plate_number: str):
    result_message = await my_garage.release_car(plate_number)

    return {'message': result_message}


@router.patch("/{plate_number}/status", response_model=MessageResponse)
async def new_status(plate_number: str, request: StatusUpdateRequest):
    result_message = await my_garage.change_status(
        plate_number, request.new_status)

    return {"message": result_message}
