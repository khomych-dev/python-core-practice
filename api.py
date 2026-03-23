from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from oop_garage import Garage

app = FastAPI()
my_darage = Garage()

class CarRegisterRequest(BaseModel):
    plate_number: str

@app.get('/')
def read_root():
    return {"message": "Welcome to the Garage API"}
