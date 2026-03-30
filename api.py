from fastapi import FastAPI, HTTPException, status, Request
from fastapi.responses import JSONResponse
from pydantic import BaseModel
from oop_garage import Garage

app = FastAPI()
my_garage = Garage()


class CarRegisterRequest(BaseModel):
    plate_number: str


class StatusUpdateRequest(BaseModel):
    new_status: str
    

@app.exception_handler(ValueError)
async def value_error_handler(request: Request, exc: ValueError):
    return JSONResponse(
        status_code=status.HTTP_400_BAD_REQUEST,
        content={
            "type": "about:blank",
            "title": "Validation Error",
            "status": 400,
            "detail": str(exc),
            "instance": str(request.url)
        }
    )


@app.get('/')
def read_root():
    return {"message": "Welcome to the Garage API"}


@app.get("/cars")
async def all_cars():
    cars_dict = await my_garage.get_all_cars()
    return cars_dict


@app.post("/cars", status_code=status.HTTP_201_CREATED)
async def register_new_car(request: CarRegisterRequest):
    result_message = await my_garage.register_car(request.plate_number)

    return {"message": result_message}


@app.delete("/cars/{plate_number}")
async def release_car_endpoint(plate_number: str):
    result_message = await my_garage.release_car(plate_number)

    return {'message': result_message}


@app.patch("/cars/{plate_number}/status")
async def new_status(plate_number: str, request: StatusUpdateRequest):
    result_message = await my_garage.change_status(
            plate_number, request.new_status)

    return {"message": result_message}