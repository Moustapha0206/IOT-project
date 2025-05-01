import time
import board
import adafruit_dht

# Use GPIO 4 (physical pin 7)
dhtDevice = adafruit_dht.DHT11(board.D17)


try:
    while True:
        temperature = dhtDevice.temperature
        humidity = dhtDevice.humidity

        if temperature is not None and humidity is not None:
            print(f"Temp: {temperature}°C  Humidity: {humidity}%")
        else:
            print("Sensor reading failed. Retrying...")

        time.sleep(2)

except KeyboardInterrupt:
    print("Stopped by User")
except Exception as e:
    print(f"Error: {e}")
finally:
    dhtDevice.exit()

