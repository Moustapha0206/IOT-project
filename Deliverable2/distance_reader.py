from gpiozero import DistanceSensor

sensor = DistanceSensor(echo=23, trigger=24)

def read_distance():
    return round(sensor.distance, 2)  # distance in meters
