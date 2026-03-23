from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from oop_garage import Garage

app = FastAPI()
my_garage = Garage()

class CarRegisterRequest(BaseModel):
    plate_number: str

@app.get('/')
def read_root():
    return {"message": "Welcome to the Garage API"}

@app.post("/cars/register")
def register_new_car(request: CarRegisterRequest):
    try:
        result_message = my_garage.register_car(request.plate_number)
        
        return {"message": result_message}
        
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))