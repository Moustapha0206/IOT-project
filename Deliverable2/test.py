from datetime import datetime
from AWSIoTPythonSDK.MQTTLib import AWSIoTMQTTClient
import config
import json
import time
from dht11_reader import read_dht11
from distance_reader import read_distance
from led_status import led_is_on
from buzzer_status import buzzer_is_on


# Set timestamp
date = datetime.now().strftime("%Y_%m_%d-%I:%M:%S_%p")
print (f"Timestamp:{date}")

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
    dht_data = read_dht11()
    payload = json.dumps({
        "temperature": dht_data["temperature"],
        "humidity": dht_data["humidity"],
        "distance": read_distance(),
        "led_on": led_is_on(),
        "buzzer_on": buzzer_is_on()
    })
    myMQTTClient.publish(config.TOPIC, payload, 1)
    loopCount += 1
    time.sleep(2)