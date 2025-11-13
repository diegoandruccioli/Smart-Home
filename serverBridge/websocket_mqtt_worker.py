# FILE: server_bridge/websocket_mqtt_worker.py
# Richiede: pip install websockets paho-mqtt

import paho.mqtt.client as mqtt
import json
import asyncio
import websockets
import threading
import time # <-- IMPORTA time
from variable import *
import database_manager as db # <-- IMPORTA IL DB MANAGER
# Non importo database o views per disaccoppiare, gestiamo solo il routing WS/MQTT qui
import traceback # <-- AGGIUNGI QUESTO IMPORT ALL'INIZIO DEL FILE
# Set globale per mantenere i riferimenti ai client WebSocket connessi
CONNECTED_WEBSOCKETS = set()

# --- Funzioni WebSocket ---

async def send_to_all_websockets(message):
    """Invia un messaggio a tutti i client WebSocket connessi."""
    if CONNECTED_WEBSOCKETS:
        # Crea un set di coroutine di invio
        send_tasks = [ws.send(message) for ws in CONNECTED_WEBSOCKETS]
        # Invia in parallelo, ignorando gli errori di connessione chiusa
        await asyncio.gather(*send_tasks, return_exceptions=True)
        # print(f"Message forwarded to {len(CONNECTED_WEBSOCKETS)} WebSocket clients.")

async def websocket_handler(websocket):
    """Gestisce la connessione e i messaggi WebSocket in arrivo dalla Dashboard."""
    CONNECTED_WEBSOCKETS.add(websocket)
    print(f"WS client connected. Total: {len(CONNECTED_WEBSOCKETS)}")
    try:
        async for message in websocket:
            # Messaggio ricevuto dalla Dashboard (Comando manuale)
            print(f"WS Command received: {message}")
            
            try:
                data = json.loads(message)
                name = data.get('name')
                measure = data.get('measure')
                
                # <-- NUOVO: Logga il comando manuale sul DB -->
                # Usiamo il timestamp attuale del server
                db.log_data(int(time.time()), name, measure)
                # <-- FINE NUOVO -->

                # Routing del comando MQTT (invariato)
                if name in ["light", "manual_light"]:
                    mqtt_client.publish(MQTT_TOPIC_COMMAND_LIGHT, message)
                    print(f"Published to {MQTT_TOPIC_COMMAND_LIGHT}: {message}")
                elif name in ["roll", "manual_roll"]:
                    mqtt_client.publish(MQTT_TOPIC_COMMAND_ROLL, message)
                    print(f"Published to {MQTT_TOPIC_COMMAND_ROLL}: {message}")
                
            except json.JSONDecodeError:
                print("Error decoding JSON from WebSocket.")
                
    except websockets.exceptions.ConnectionClosedOK:
        pass
    finally:
        CONNECTED_WEBSOCKETS.remove(websocket)
        print(f"WS client disconnected. Total: {len(CONNECTED_WEBSOCKETS)}")

# --- Funzioni MQTT ---

# AGGIUNGI *args per catturare argomenti non necessari (come 'properties')
# Questa firma è più robusta con le versioni 1.x e 2.x
def on_connect(client, userdata, flags, reason_code, *args):
    """Callback chiamata alla connessione MQTT."""
    print("MQTT Connected. Subscribing to sensor topics.")
    for topic in MQTT_TOPIC_SENSORS:
        client.subscribe(topic)
        print(f"Subscribed to {topic}")

def on_message(client, userdata, msg):
    """Callback chiamata alla ricezione di un messaggio MQTT (Dati Sensori)."""
    payload = msg.payload.decode("utf-8")
    # print(f"MQTT Data received ({msg.topic}): {payload}")

    try:
        # <-- NUOVO: Logga i dati del sensore sul DB -->
        data = json.loads(payload)
        # Il timestamp e i dati provengono direttamente dall'ESP
        db.log_data(data.get('timestamp'), data.get('name'), data.get('measure'))
        # <-- FINE NUOVO -->
    except json.JSONDecodeError:
        print("Errore nel payload MQTT, non è JSON valido.")
    except Exception as e:
        print(f"Errore durante il logging MQTT: {e}")


    # 1. Inoltra ai client WebSocket (per la Dashboard)
    asyncio.run(send_to_all_websockets(payload))

    # 2. Logica di persistenza rimossa da qui (ora gestita sopra)
    """Callback chiamata alla ricezione di un messaggio MQTT (Dati Sensori)."""
    payload = msg.payload.decode("utf-8")
    # print(f"MQTT Data received ({msg.topic}): {payload}")

    # 1. Inoltra ai client WebSocket (per la Dashboard)
    # Dobbiamo eseguire la funzione asincrona in modo sincrono/thread-safe
    asyncio.run(send_to_all_websockets(payload))

# 2. Logica di persistenza rimossa da qui (ora gestita sopra)

# Variabile globale per il client MQTT
mqtt_client = mqtt.Client()
mqtt_client.on_connect = on_connect
mqtt_client.on_message = on_message

def run_mqtt_client():
    """Connessione e loop MQTT in un thread separato."""
    try:
        mqtt_client.tls_set() 
        
        # --- MODIFICA QUESTA PARTE ---
        # Aggiungi le credenziali da variable.py
        if MQTT_USER and MQTT_PASS:
            mqtt_client.username_pw_set(MQTT_USER, MQTT_PASS)
            print(f"MQTT: Trovate credenziali, connessione con utente: {MQTT_USER}")
        else:
            print("MQTT: Attenzione, utente/password non impostati in variable.py. Connessione anonima.")
        
        mqtt_client.connect(MQTT_URL, MQTT_PORT, 60)
        mqtt_client.loop_forever()
    except Exception as e:
        print(f"MQTT Client Error: {e}")

# FILE: serverBridge/websocket_mqtt_worker.py
# ... (tutto il codice fino alla funzione run() rimane invariato) ...

async def main():
    """Funzione asincrona principale per avviare il server WebSocket."""
    print(f"WebSocket server starting at ws://{WEBSOCKET_HOST}:{WEBSOCKET_PORT}")
    
    # Avvia il server usando il pattern 'async with'
    async with websockets.serve(websocket_handler, WEBSOCKET_HOST, WEBSOCKET_PORT):
        # Il server è in esecuzione.
        # Ora dobbiamo tenerlo in esecuzione per sempre.
        await asyncio.Future()  # Questo "dorme" all'infinito, tenendo vivo il server

def run():
    """Avvia il bridge completo (MQTT in thread, WebSocket nel main thread asincrono)."""
    
    print("Inizializzazione del database...")
    db.init_db()
    
    mqtt_thread = threading.Thread(target=run_mqtt_client, daemon=True)
    mqtt_thread.start()
    print("MQTT Client started in background thread.")

    try:
        # Questo è il comando che sta fallendo.
        asyncio.run(main())
        
    except RuntimeError as e:
        print(f"--- ERRORE RUNTIME ASYNCIO ---")
        print(f"Messaggio: {e}")
        # Stampiamo il traceback completo per capire da DOVE origina
        traceback.print_exc()
        print(f"---------------------------------")
        
    except OSError as e:
        if e.errno == 10048: # Address already in use
             print(f"ERRORE: La porta {WEBSOCKET_PORT} è già in uso. Chiudi altri processi.")
        else:
             print(f"Errore OS: {e}")
             traceback.print_exc()
    
    except Exception as e:
        print(f"--- ERRORE GENERICO NEL WORKER ---")
        print(f"Messaggio: {e}")
        traceback.print_exc()
        print(f"----------------------------------")

if __name__ == '__main__':
    run()