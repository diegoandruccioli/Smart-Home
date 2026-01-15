# ---
# FILE: serverBridge/variable.py
# OBIETTIVO: Configurazione centrale
# ---

import os 

# --- Percorsi ---
_PROJECT_ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))

# --- Configurazione Database ---
DB_URL = "" 
DB_NAME = os.path.join(_PROJECT_ROOT, "smart_home.db")
DB_TABLE = "SmartHome" 

# --- Configurazione MQTT (HiveMQ) ---
MQTT_URL = "52dddef9726d430db26ad9b27548f562.s1.eu.hivemq.cloud" 
MQTT_PORT = 8883

# --- Credenziali MQTT ---
MQTT_USER = "bothrei" 
MQTT_PASS = "Bothrei1" 

# --- Topic (Canali) MQTT ---

# MODIFICATO: Il server ora ascolta SIA i sensori grezzi (sensor/) SIA i canali attuatore (esp/)
MQTT_TOPIC_SENSORS = [
    "sensor/temperature", 
    "sensor/motion", 
    "esp/temperature", 
    "esp/motion"
]

# Topic Comandi
MQTT_TOPIC_COMMAND_LIGHT = "cmd/light"
MQTT_TOPIC_COMMAND_ROLL = "cmd/roll"

# --- Configurazione WebSocket ---
WEBSOCKET_HOST = "0.0.0.0"
WEBSOCKET_PORT = 8080