import aiosqlite
from config import settings

class Garage:
        
    async def release_car(self, plate_number: str) -> str:
        clean_plates_list = self._clean_plates([plate_number])
        if not clean_plates_list:
            raise ValueError("Invalid plate format.")
        
        clean_plate = clean_plates_list[0]
        
        async with aiosqlite.connect(settings.db_path) as db:
            cursor = await db.execute("SELECT status FROM cars WHERE plate_number = ?", (clean_plate,))
            
            row = await cursor.fetchone()
            if row is None:
                raise ValueError(f"The car plate_number {plate_number} was not found")
        
            elif row[0] != 'repair completed':
                raise ValueError("Cannot release the car. It is still in repair.")
            
            await db.execute(
                "DELETE FROM cars WHERE plate_number = ?", (clean_plate,))
            
            await db.commit()
            return f"The vehicle with license plate number {plate_number} has been successfully returned to its owner"
    
    async def register_car(self, plate_number: str, brand: str) -> str:
        clean_plates_list = self._clean_plates([plate_number])
        if not clean_plates_list:
            raise ValueError("Invalid plate format. Registration failed.")
        
        clean_plate = clean_plates_list[0]
        async with aiosqlite.connect(settings.db_path) as db:
            try:
                await db.execute(
                    "INSERT INTO cars(plate_number, brand, status) VALUES (?,?,?)", (clean_plate, brand, 'in repair')
                    )
                await db.commit()
                return f"Car {clean_plate} registered successfully in DB!"
            
            except aiosqlite.IntegrityError:
                raise ValueError(f"The car {clean_plate} is already registered!")
    
    def _clean_plates(self, plates: list[str]) -> list[str]:
        result = []
        for plate in plates:
            clean_plate = str(plate).upper().strip().replace(" ", "")
            if 3 <= len(clean_plate) <= 8:
                result.append(clean_plate)
         
        return result
    
    async def change_status(self, plate_number: str, new_status: str) -> str:
        clean_plates_list = self._clean_plates([plate_number])
        if not clean_plates_list:
            raise ValueError("Invalid plate format.")
        
        clean_plate = clean_plates_list[0]
        async with aiosqlite.connect(settings.db_path) as db:
            cursor = await db.execute("SELECT plate_number FROM cars WHERE plate_number = ?", (clean_plate,))
            
            row = await cursor.fetchone()
            if row is None:
                raise ValueError(f"The car plate_number {plate_number} was not found")

            await db.execute("UPDATE cars SET status = ? WHERE plate_number = ?", (new_status, clean_plate))
            
            await db.commit()
            return f"The status of the vehicle with license plate number {plate_number}  has been successfully updated"
    
    async def get_all_cars(self) -> dict[str, dict[str, str]]:
        async with aiosqlite.connect(settings.db_path) as db:
            cursor = await db.execute("SELECT plate_number, brand, status FROM cars")
            
            rows = await cursor.fetchall()
            result_dict = {plate: {"brand": brand,"status": status} for plate, brand, status in rows}
            
            return result_dict