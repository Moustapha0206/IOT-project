import board
import adafruit_dht

dhtDevice = adafruit_dht.DHT11(board.D17)

def read_dht11():
    try:
        temperature = dhtDevice.temperature
        humidity = dhtDevice.humidity
        return {"temperature": temperature, "humidity": humidity}
    except:
        return {"temperature": None, "humidity": None}
