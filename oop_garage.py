import json

class Garage:
    def __init__(self, filename='garage.json'):
        self.filename = filename
        self.db = self._load_garage()

    def _load_garage(self):
        try:
            with open(self.filename, 'r', encoding='utf-8') as f:
                data = json.load(f)
                return data
      
        except FileNotFoundError:
            return {}
    
    def save(self):
      with open(self.filename, 'w', encoding='utf-8') as f:
         json.dump(self.db, f, indent=4, ensure_ascii=False)
        
    def release_car(self, plate_number):
        if plate_number in self.db :
            if self.db[plate_number] == 'repair completed':
                del self.db[plate_number]
                self.save()
                return f"The vehicle with license plate number {plate_number} has been successfully returned to its owner"
            return "Cannot release the car. It is still in repair."
        return f"The car plate_number {plate_number} was not found"
    
    def register_car(self, plate_number, status='in repair'):
        for plate in self._clean_plates([plate_number]):
            self.db[plate] = status
            self.save()
            return f"The car {plate_number} has been successfully registered"
        return "Invalid plate format. Registration failed."
    
    def _clean_plates(self, plates):
        result = []
        for plate in plates:
            clean_plate = str(plate).upper().strip().replace(" ", "")
            if 3 <= len(clean_plate) <= 8:
                result.append(clean_plate)
         
        return result
    
    def change_status(self, plate_number, new_status):
        if plate_number in self.db:
            self.db[plate_number] = new_status
            self.save()
            return f"Status changed to '{new_status}'"
        return f"The car plate_number {plate_number} was not found"
    
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