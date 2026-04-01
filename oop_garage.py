from sqlalchemy.exc import IntegrityError
from sqlalchemy import select
from database import AsyncSessionLocal
from models import CarDB

class Garage:
        
    async def release_car(self, plate_number: str) -> str:
        clean_plate = self._clean_plate(plate_number)
        
        async with AsyncSessionLocal() as session:
            stmt = select(CarDB).where(CarDB.plate_number == clean_plate)
            result = await session.execute(stmt)
            car = result.scalar_one_or_none()
            
            if not car:
                raise ValueError(f"Car {clean_plate} not found in Garage!")
        
            if car.status != "repaired":
                raise ValueError(f"Cannot release car {clean_plate}. Current status is '{car.status}'. Only 'repaired' cars can be released.")
        
            await session.delete(car)
            await session.commit()
            
            return f"Car {clean_plate} released successfully!"
    
    async def register_car(self, plate_number: str, brand: str) -> str:
        clean_plate = self._clean_plate(plate_number)
        
        async with AsyncSessionLocal() as session:
            try:
                new_car = CarDB(plate_number=clean_plate, brand=brand, status='in repair')
                session.add(new_car)
                await session.commit()
                
                return f"Car {clean_plate} registered successfully in DB!"
            
            except IntegrityError:
                await session.rollback()
                raise ValueError(f"The car {clean_plate} is already registered!")
                
                
    def _clean_plate(self, plate: str) -> str:
        clean = plate.upper().replace(" ", "")
        if 3 <= len(clean) <= 8:
            return clean
        
        raise ValueError("Invalid plate format.")
    
    async def change_status(self, plate_number: str, new_status: str) -> str:
        clean_plate = self._clean_plate(plate_number)
        
        async with AsyncSessionLocal() as session:
            stmt = select(CarDB).where(CarDB.plate_number == clean_plate)
            result = await session.execute(stmt)
            car = result.scalar_one_or_none()
            
            if not car:
                raise ValueError(f"Car {clean_plate} not found in Garage!")

            car.status = new_status
            await session.commit()
            
            return f"Status of {clean_plate} changed to {new_status}"
    
    async def get_all_cars(self) -> dict[str, dict[str, str]]:
        async with AsyncSessionLocal() as session:
            stmt = select(CarDB)
            
            result = await session.execute(stmt)
            
            cars = result.scalars().all()
            
            return {
                car.plate_number:
                    {"brand": car.brand, "status": car.status} for car in cars
                }