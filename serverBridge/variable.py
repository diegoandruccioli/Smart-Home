# ---
# FILE: serverBridge/variable.py
#
# OBIETTIVO:
# Questo file è il "Centro di Configurazione" dell'applicazione.
# Contiene tutte le costanti (come URL, porte, nomi dei topic) 
# in un unico posto, in modo da non doverle scrivere a mano
# nel codice (evitando errori).
# ---

# Importa 'os' per permettere la gestione dei percorsi di file
import os 

# --- Calcola il percorso della cartella radice (Smart-Home) ---

# '__file__' è una variabile speciale di Python che contiene il percorso di *questo* file
# (es. 'C:/.../Smart-Home/serverBridge/variable.py')
#
# 'os.path.dirname(__file__)' ottiene solo la cartella
# (es. 'C:/.../Smart-Home/serverBridge')
#
# 'os.path.join(..., '..')' aggiunge '..' al percorso, che significa "torna indietro di una cartella"
# (es. 'C:/.../Smart-Home')
#
# 'os.path.abspath()' pulisce il percorso e lo rende assoluto
_PROJECT_ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))


# --- Configurazione Database ---

# URL per un database SQL complesso (es. MySQL, Postgres). Inutilizzato per SQLite.
DB_URL = "" 

# VECCHIO: DB_NAME = "smart_home.db" (creava il file in serverBridge/)
# NUOVO: Unisce il percorso 'Smart-Home' al nome del file
# (risultato: 'C:/.../Smart-Home/smart_home.db')
DB_NAME = os.path.join(_PROJECT_ROOT, "smart_home.db")

# Nome della tabella (NOTA: nel tuo file hai 'SmartHome', ma database_manager.py
# usa 'sensor_data'. Questa riga è probabilmente un refuso non utilizzato).
DB_TABLE = "SmartHome" 

# --- Configurazione MQTT (per HiveMQ) ---

# L'indirizzo pubblico del tuo broker MQTT su HiveMQ
MQTT_URL = "52dddef9726d430db26ad9b27548f562.s1.eu.hivemq.cloud" 
# La porta per la connessione sicura (SSL/TLS)
MQTT_PORT = 8883

# (Ho CANCELLATO la riga 'DB_NAME = "smart_home.db"' che avevi qui perché era un errore)

# --- Credenziali MQTT ---
# Devi inserire qui lo username e la password che usi anche sull'ESP32
MQTT_USER = "bothrei" # <-- Metti lo stesso user che hai in main.cpp
MQTT_PASS = "Bothrei1" # <-- Metti la stessa password

# --- Topic (Canali) MQTT ---

# Lista dei topic su cui il worker Python si mette in *ascolto*
# (Dati inviati dalla scheda sensori)
MQTT_TOPIC_SENSORS = ["esp/light", "esp/motion"]

# Topic su cui il worker Python *scrive* (pubblica)
# (Comandi inviati dalla dashboard)
MQTT_TOPIC_COMMAND_LIGHT = "cmd/light"
MQTT_TOPIC_COMMAND_ROLL = "cmd/roll"

# --- Configurazione WebSocket (per la Dashboard) ---

# Indirizzo IP su cui il server WebSocket deve ascoltare
# '0.0.0.0' è un indirizzo speciale che significa "ascolta su tutte le interfacce"
# (sia localhost, sia l'IP di rete locale)
WEBSOCKET_HOST = "0.0.0.0"
# La porta dedicata al server WebSocket (deve essere DIVERSA da quella di Flask)
WEBSOCKET_PORT = 8080