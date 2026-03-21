import pytest
import os
from oop_garage import Garage

@pytest.fixture
def temp_garage():
    test_file = "test_test_db.json"
    garage = Garage(filename=test_file)
    
    yield garage
    
    if os.path.exists(test_file):
        os.remove(test_file)

def test_register_car_success(temp_garage):
    temp_garage.register_car("AA1111BB")
    
    assert "AA1111BB" in temp_garage.db
        
def test_register_car_duplicate():
    test_file = "test_test_db.json"
    garage = Garage(filename=test_file)
    garage.register_car("AA1111BB")
    
    with pytest.raises(ValueError):
        garage.register_car("AA1111BB")
        
    if os.path.exists(test_file):
        os.remove(test_file)
    
def test_release_car_not_found():
    test_file = "test_test_db.json"
    garage = Garage(filename=test_file)
    garage.register_car("AA1111BB")
    
    with pytest.raises(ValueError):
        garage.release_car("SS999H")
        
    if os.path.exists(test_file):
        os.remove(test_file)
        
test_register_car_success(temp_garage())