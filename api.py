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

@app.post("/cars/register")
def register_new_car(request: CarRegisterRequest):
    try:
        result_message = my_garage.register_car(request.plate_number)
        
        return {"message": result_message}
        
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    
@app.delete("/cars/{plate_number}")
def release_car_endpoint(plate_number: str):
    try:
        result_message = my_garage.release_car(plate_number)
        
        return {'message': result_message}
    
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))