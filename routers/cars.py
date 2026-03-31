from fastapi import APIRouter, status
from oop_garage import Garage
from pydantic import BaseModel

router = APIRouter(prefix="/api/v1/cars")
my_garage = Garage()

class CarRegisterRequest(BaseModel):
    plate_number: str


class StatusUpdateRequest(BaseModel):
    new_status: str
    
    
class MessageResponse(BaseModel):
    message: str


@router.get("/")
async def all_cars():
    cars_dict = await my_garage.get_all_cars()
    return cars_dict


@router.post("/", status_code=status.HTTP_201_CREATED, response_model=MessageResponse)
async def register_new_car(request: CarRegisterRequest):
    result_message = await my_garage.register_car(request.plate_number)

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