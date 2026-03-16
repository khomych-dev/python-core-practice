def list_numbers(numbers):
   result = [n for n in numbers if n % 2 == 0 and n != 0]
   return result
    
numbers = [1, 2, 0, 4, 5, 0, 8]
print(list_numbers(numbers))