# FILE: server_bridge/websocket_mqtt_worker.py
# Richiede: pip install websockets paho-mqtt

import paho.mqtt.client as mqtt
import json
import asyncio
import websockets
import threading
from variable import *
# Non importo database o views per disaccoppiare, gestiamo solo il routing WS/MQTT qui

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

async def websocket_handler(websocket, path):
    """Gestisce la connessione e i messaggi WebSocket in arrivo dalla Dashboard."""
    CONNECTED_WEBSOCKETS.add(websocket)
    print(f"WS client connected. Total: {len(CONNECTED_WEBSOCKETS)}")
    try:
        async for message in websocket:
            # Messaggio ricevuto dalla Dashboard (Comando manuale)
            print(f"WS Command received: {message}")
            
            # Pubblica il comando manuale su MQTT (per la scheda Attuatori)
            try:
                data = json.loads(message)
                name = data.get('name')
                
                # Routing del comando MQTT
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

def on_connect(client, userdata, flags, reason_code, properties):
    """Callback chiamata alla connessione MQTT."""
    print("MQTT Connected. Subscribing to sensor topics.")
    for topic in MQTT_TOPIC_SENSORS:
        client.subscribe(topic)
        print(f"Subscribed to {topic}")

def on_message(client, userdata, msg):
    """Callback chiamata alla ricezione di un messaggio MQTT (Dati Sensori)."""
    payload = msg.payload.decode("utf-8")
    # print(f"MQTT Data received ({msg.topic}): {payload}")

    # 1. Inoltra ai client WebSocket (per la Dashboard)
    # Dobbiamo eseguire la funzione asincrona in modo sincrono/thread-safe
    asyncio.run(send_to_all_websockets(payload))

    # 2. Qui andrebbe la logica di persistenza nel DB (es. views.persist_data(payload))

# Variabile globale per il client MQTT
mqtt_client = mqtt.Client(mqtt.CallbackAPIVersion.VERSION2)
mqtt_client.on_connect = on_connect
mqtt_client.on_message = on_message

def run_mqtt_client():
    """Connessione e loop MQTT in un thread separato."""
    try:
        mqtt_client.connect(MQTT_URL, MQTT_PORT, 60)
        mqtt_client.loop_forever()
    except Exception as e:
        print(f"MQTT Client Error: {e}")

def run():
    """Avvia il bridge completo (MQTT in thread, WebSocket nel main thread asincrono)."""
    # Avvia il client MQTT in un thread per non bloccare asyncio
    mqtt_thread = threading.Thread(target=run_mqtt_client, daemon=True)
    mqtt_thread.start()
    print("MQTT Client started in background thread.")

    # Avvia il server WebSocket nel main thread asincrono
    start_server = websockets.serve(websocket_handler, WEBSOCKET_HOST, WEBSOCKET_PORT)
    print(f"WebSocket server starting at ws://{WEBSOCKET_HOST}:{WEBSOCKET_PORT}")
    asyncio.get_event_loop().run_until_complete(start_server)
    asyncio.get_event_loop().run_forever()


if __name__ == '__main__':
    run()