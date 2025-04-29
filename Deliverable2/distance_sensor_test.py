from gpiozero import DistanceSensor
from time import sleep

# Initialize distance sensor - adjust pins as needed
sensor = DistanceSensor(echo=23, trigger=24)

print("Testing Distance Sensor module")
print("Will continuously measure distance (Ctrl+C to stop)")

try:
    while True:
        distance = sensor.distance * 100  # Convert to centimeters
        print(f'Distance: {distance:.2f} cm')
        sleep(1)
except KeyboardInterrupt:
    print("\nTest stopped by user")