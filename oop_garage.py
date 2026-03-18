from task_1 import load_garage

class Garage:
    def __init__(self, filename='garage.json'):
        self.filename = filename
        self.db = load_garage(self.filename)
