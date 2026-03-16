def clean_plates(plates):
   result = []
   for i in plates:
      i = str(i).upper().strip()
      if len(i) == 8:
         result.append(i)
         
   return result
      
plates = ["  aa1234bb ", "invalid_plate", "XX9999XX", " a b c ", "kH0mycH1"]
print(clean_plates(plates))
