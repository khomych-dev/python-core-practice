from task_1 import load_garage
from task_1 import save_garage
from task_1 import clean_plates

class Garage:
    def __init__(self, filename='garage.json'):
        self.filename = filename
        self.db = load_garage(self.filename)

    def save(self):
        save_garage(self.db, self.filename)
        
    def release_car(self, plate_number):
        if plate_number in self.db:
            del self.db[plate_number]
            self.save()
            return f"The vehicle with license plate number {plate_number} has been successfully returned to its owner"
        return f"The car plate_number {plate_number} was not found"
    
    def register_car(self, plate_number, status='in repair'):
        for plate in clean_plates([plate_number]):
            self.db[plate] = status
            self.save()
            return f"The car {plate_number} has been successfully registered"
        return "Invalid plate format. Registration failed."