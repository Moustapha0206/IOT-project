from datetime import datetime
from AWSIoTPythonSDK.MQTTLib import AWSIoTMQTTClient
import config
import json
import time
from main import read_temp, dht_device, lid_sensor, status_led, buzzer

# Set timestamp
date = datetime.now().strftime("%Y_%m_%d-%I:%M:%S_%p")
print(f"Timestamp:{date}")

# User specified callback function
def customCallback(client, userdata, message):
    print("Received a new message: ")
    print(message.payload)
    print("from topic: ")
    print(message.topic)
    print("--------------\n\n")

# Configure the MQTT client
myMQTTClient = AWSIoTMQTTClient(config.CLIENT_ID)
myMQTTClient.configureEndpoint(config.AWS_HOST, config.AWS_PORT)
myMQTTClient.configureCredentials(config.AWS_ROOT_CA, config.AWS_PRIVATE_KEY, config.AWS_CLIENT_CERT)
myMQTTClient.configureConnectDisconnectTimeout(config.CONN_DISCONN_TIMEOUT)
myMQTTClient.configureMQTTOperationTimeout(config.MQTT_OPER_TIMEOUT)

# Connect to MQTT Host
if myMQTTClient.connect():
    print('AWS connection succeeded')

# Subscribe to topic
myMQTTClient.subscribe(config.TOPIC, 1, customCallback)
time.sleep(2)

# Send message to host
loopCount = 0
while loopCount < 10:
    temperature = read_temp()
    try:
        humidity = dht_device.humidity
    except:
        humidity = None
    try:
        distance = round(lid_sensor.distance * 100, 2)
    except:
        distance = None

    payload = json.dumps({
        "temperature": temperature,
        "humidity": humidity,
        "lid_open": distance > 10 if distance is not None else None,
        "led_on": status_led.value == 1,
        "buzzer_on": buzzer.value == 1
    })

    myMQTTClient.publish(config.TOPIC, payload, 1)
    print("Published payload:", payload)

    loopCount += 1
    time.sleep(2)
