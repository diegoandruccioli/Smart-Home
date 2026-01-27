import os 

_PROJECT_ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))

DB_URL = "" 
DB_NAME = os.path.join(_PROJECT_ROOT, "smart_home.db")
DB_TABLE = "SmartHome" 

MQTT_URL = "52dddef9726d430db26ad9b27548f562.s1.eu.hivemq.cloud" 
MQTT_PORT = 8883

MQTT_USER = "bothrei" 
MQTT_PASS = "Bothrei1" 


# il server ascolta SIA i sensori grezzi (sensor/) SIA i canali attuatore (esp/)
MQTT_TOPIC_SENSORS = [
    "sensor/temperature", 
    "sensor/motion", 
    "esp/temperature", 
    "esp/motion"
]

MQTT_TOPIC_COMMAND_LIGHT = "cmd/light"
#MQTT_TOPIC_COMMAND_ROLL = "cmd/roll"

WEBSOCKET_HOST = "0.0.0.0"
WEBSOCKET_PORT = 8080