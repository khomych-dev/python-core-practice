from fastapi import FastAPI
from oop_garage import Garage

app = FastAPI()

my_darage = Garage()

@app.get('/')
def read_root():
    return {"message": "Welcome to the Garage API"}