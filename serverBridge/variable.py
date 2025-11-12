# FILE: server_bridge/variable.py

# --- Database Config (Mantieni i tuoi valori) ---
DB_URL = "" 
DB_NAME = "SmartHome"
DB_TABLE = "SmartHomeData" 

# --- MQTT Config (Mantieni i tuoi valori) ---
MQTT_URL = "6a7c8e41ebb842f4811d5f9e75cdffc4.s1.eu.hivemq.cloud" # Indirizzo del MQTT Broker (es. Mosquitto)
MQTT_PORT = 8883

# TOPIC SENSORS (Pubblicati dalla Scheda Sensori, Sottoscritti qui)
MQTT_TOPIC_SENSORS = ["esp/light", "esp/motion"] 

# TOPIC COMMANDS (Pubblicati qui, Sottoscritti dalla Scheda Attuatori)
MQTT_TOPIC_COMMAND_LIGHT = "cmd/light"
MQTT_TOPIC_COMMAND_ROLL = "cmd/roll"

# --- WebSocket Config (Frontend Dashboard) ---
WEBSOCKET_HOST = "0.0.0.0"  # Ascolta su tutte le interfacce
WEBSOCKET_PORT = 8080