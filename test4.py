import threading
import time

# Define the base class
class Vehicle(threading.Thread):
    def __init__(self, name):
        super(Vehicle, self).__init__(name=name)  # Pass the name to the Thread constructor

    def run(self):
        while True:
            print(f'running thread...{self.name}')
            time.sleep(2)

    def change_name(self, new_name):
        self.name = new_name  # Modify the name attribute of the Thread object

    def stop_engine(self):
        print(f"{self.name} engine stopped.")

# Define the derived class inheriting from Vehicle
class Car(Vehicle):
    def __init__(self, speed):
        self.speed = speed
        super(Car, self).__init__('')  # Pass an empty name to the base class constructor

    def race(self):
        print('in race changing name..')
        self.change_name('qwerty')  # Call the parent class method to modify the name
        obj.name = 'qwertyui'

# Create a Vehicle object
obj = Vehicle('ravi')
obj.start()

time.sleep(5)

# Create a Car object
car1 = Car(60)
car1.race()
