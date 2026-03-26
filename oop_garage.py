import aiosqlite

class Garage:
    def __init__(self, filename='garage.json'):
        self.filename = filename
        
    async def release_car(self, plate_number):
        clean_plates_list = self._clean_plates([plate_number])
        if not clean_plates_list:
            raise ValueError("Invalid plate format.")
        
        clean_plate = clean_plates_list[0]
        
        async with aiosqlite.connect("garage.db") as db:
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
    
    async def register_car(self, plate_number: str):
        clean_plates_list = self._clean_plates([plate_number])
        if not clean_plates_list:
            raise ValueError("Invalid plate format. Registration failed.")
        
        clean_plate = clean_plates_list[0]
        async with aiosqlite.connect("garage.db") as db:
            try:
                await db.execute(
                    "INSERT INTO cars(plate_number, status) VALUES (?,?)", (clean_plate, 'in repair')
                    )
                await db.commit()
                return f"Car {clean_plate} registered successfully in DB!"
            
            except aiosqlite.IntegrityError:
                raise ValueError(f"The car {clean_plate} is already registered!")
    
    def _clean_plates(self, plates):
        result = []
        for plate in plates:
            clean_plate = str(plate).upper().strip().replace(" ", "")
            if 3 <= len(clean_plate) <= 8:
                result.append(clean_plate)
         
        return result
    
    async def change_status(self, plate_number, new_status):
        clean_plates_list = self._clean_plates([plate_number])
        if not clean_plates_list:
            raise ValueError("Invalid plate format.")
        
        clean_plate = clean_plates_list[0]
        async with aiosqlite.connect("garage.db") as db:
            cursor = await db.execute("SELECT plate_number FROM cars WHERE plate_number = ?", (clean_plate,))
            
            row = await cursor.fetchone()
            if row is None:
                raise ValueError(f"The car plate_number {plate_number} was not found")

            await db.execute("UPDATE cars SET status = ? WHERE plate_number = ?", (new_status, clean_plate))
            
            await db.commit()
            return f"The status of the vehicle with license plate number {plate_number}  has been successfully updated"
        
        
        if plate_number in self.db:
            self.db[plate_number] = new_status
            self.save()
            return f"Status changed to '{new_status}'"
        return f"The car plate_number {plate_number} was not found"
    
    async def get_all_cars(self):
        async with aiosqlite.connect("garage.db") as db:
            cursor = await db.execute("SELECT * FROM cars")
            
            rows = await cursor.fetchall()
            result_dict = {plate: status for plate, status in rows}
            
            return result_dict

if __name__ == '__main__':
    
    my_garage = Garage()
    
    while True:
        action = input("\nEnter the command: ").lower()
    
        if action == 'exit':
            break
    
        if action == 'change status':
            plate_num = input("Enter your license plate number: ").upper()
            new_status = input("Enter new status: ")
            print(my_garage.change_status(plate_num, new_status))

            continue
        
        if action == 'register':
            plate_num = input("Enter your license plate number: ").upper()
            print(my_garage.register_car(plate_num))

            continue
    
        if action == "return the car":
            plate_num = input("Enter your license plate number: ").upper()
            print(my_garage.release_car(plate_num))

            continue
  
        else:
            print("Unknown command. Try again.")