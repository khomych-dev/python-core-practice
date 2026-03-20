import os
from oop_garage import Garage

def test_register_car_success():
    test_file = "test_test_db.json"
    garage = Garage(filename=test_file)
    
    garage.register_car("AA1111BB")
    
    assert "AA1111BB" in garage.db
    
    if os.path.exists(test_file):
        os.remove(test_file)