import json

def clean_plates(plates):
   result = []
   for plate in plates:
      clean_plate = str(plate).upper().strip()
      if 3 <= len(clean_plate) <= 8:
         result.append(clean_plate)
         
   return result

def register_cars(clean_plates, status="in repair"):
   my_garage = load_garage()
   for plat in clean_plates:
      my_garage[plat] = status
      
   return my_garage

def release_car(garage_db, plate_number):
   if plate_number in garage_db:
      del garage_db[plate_number]
      print(f"The car {plate_number} has been successfully issued")
      return garage_db
      
   print(f"The car plate_number {plate_number} was not found")
   return garage_db

def save_garage(data, filename='garage.json'):
      with open(filename, 'w', encoding='utf-8') as f:
         json.dump(data, f, indent=4, ensure_ascii=False)
         
def load_garage(filename='garage.json'):
   try:
      with open(filename, 'r', encoding='utf-8') as f:
         data = json.load(f)
         return data
      
   except FileNotFoundError:
      return {}

garage = load_garage()

while True:
   action = input("Enter the command: ").lower()
   if action == 'exit':
      break
   
   if action == "return the car":
      plate_num = input("Enter your license plate number: ").upper()
      garage = release_car(garage, plate_num)
      save_garage(garage)
   
   if action == "register cars":
      plate_num = input("Enter your license plate number: ").upper()
      clean = clean_plates(plate_num)
      garage = register_cars(clean)
      save_garage(garage)
   
print("Unknown command. Try again.")         
print(load_garage())