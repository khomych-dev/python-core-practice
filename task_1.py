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
   
plates = ["  aa1234bb ", "invalid_plate", "XX9999XX", " a b c ", "kH0mycH1"]
cleaned_data = clean_plates(plates)
print(register_cars(cleaned_data))