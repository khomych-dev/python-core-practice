from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from oop_garage import Garage

app = FastAPI()
my_garage = Garage()


class CarRegisterRequest(BaseModel):
    plate_number: str


class StatusUpdateRequest(BaseModel):
    new_status: str


@app.get('/')
def read_root():
    return {"message": "Welcome to the Garage API"}


@app.get("/cars")
async def all_cars():
    cars_dict = await my_garage.get_all_cars()
    return cars_dict


@app.post("/cars/register")
async def register_new_car(request: CarRegisterRequest):
    try:
        result_message = await my_garage.register_car(request.plate_number)

        return {"message": result_message}

    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))


@app.delete("/cars/{plate_number}")
async def release_car_endpoint(plate_number: str):
    try:
        result_message = await my_garage.release_car(plate_number)

        return {'message': result_message}

    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))


@app.patch("/cars/{plate_number}/status")
async def new_status(plate_number: str, request: StatusUpdateRequest):
    try:
        result_message = await my_garage.change_status(
            plate_number, request.new_status)

        return {"message": result_message}

    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
