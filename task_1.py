def clean_plates(plates):
   result = []
   for plate in plates:
      clean_plate = str(plate).upper().strip()
      if 3 <= len(clean_plate) <= 8:
         result.append(clean_plate)
         
   return result

def register_cars(clean_plates, status="in repair"):
   my_garage = {}
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

plates = ["  aa1234bb ", "invalid_plate", "XX9999XX", " a b c ", "kH0mycH1"]
cleaned_data = clean_plates(plates)
garage_db = register_cars(cleaned_data)

while True:
   action = input("Enter the command: ").lower()
   if action == 'return the car':
      plate_num = input("Enter your license plate number: ").upper()
      if plate_num in garage_db:
         release_car(garage_db, plate_num)
         break
         
print(garage_db)