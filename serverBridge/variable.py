# FILE: server_bridge/variable.py

# --- Database Config (Mantieni i tuoi valori) ---
DB_URL = "172.20.10.8" 
DB_NAME = "tuoDB"
DB_TABLE = "SmartHomeData" 

# --- MQTT Config (Mantieni i tuoi valori) ---
MQTT_URL = "172.20.10.8" # Indirizzo del tuo MQTT Broker (es. Mosquitto)
MQTT_PORT = 1883

# TOPIC SENSORS (Pubblicati dalla Scheda Sensori, Sottoscritti qui)
MQTT_TOPIC_SENSORS = ["esp/light", "esp/motion"] 

# TOPIC COMMANDS (Pubblicati qui, Sottoscritti dalla Scheda Attuatori)
MQTT_TOPIC_COMMAND_LIGHT = "cmd/light"
MQTT_TOPIC_COMMAND_ROLL = "cmd/roll"

# --- WebSocket Config (Frontend Dashboard) ---
WEBSOCKET_HOST = "0.0.0.0"  # Ascolta su tutte le interfacce
WEBSOCKET_PORT = 8080