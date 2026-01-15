# ---
# OBIETTIVO:
# Questo è il "Worker Process". Gestisce WebSocket e MQTT.
# ---

import paho.mqtt.client as mqtt
import json
import asyncio
import websockets
import threading
import time 
from variable import *
import database_manager as db
import traceback

# --- Gestione Client WebSocket ---

CONNECTED_WEBSOCKETS = set()

async def send_to_all_websockets(message):
    """Invia un messaggio a tutti i client WebSocket connessi."""
    if CONNECTED_WEBSOCKETS:
        send_tasks = [ws.send(message) for ws in CONNECTED_WEBSOCKETS]
        await asyncio.gather(*send_tasks, return_exceptions=True)

async def websocket_handler(websocket):
    """Gestisce un singolo client WebSocket."""
    CONNECTED_WEBSOCKETS.add(websocket)
    print(f"WS client connected. Total: {len(CONNECTED_WEBSOCKETS)}")
    
    try:
        async for message in websocket:
            print(f"WS Command received: {message}")
            try:
                data = json.loads(message)
                name = data.get('name')
                measure = data.get('measure')
                
                # 1. Log sul DB
                db.log_data(int(time.time()), name, measure)

                # 2. Inoltro a MQTT
                if name in ["light", "manual_light"]:
                    mqtt_client.publish(MQTT_TOPIC_COMMAND_LIGHT, message)
                    print(f"Published to {MQTT_TOPIC_COMMAND_LIGHT}: {message}")
                elif name in ["roll", "manual_roll"]:
                    mqtt_client.publish(MQTT_TOPIC_COMMAND_ROLL, message)
                    print(f"Published to {MQTT_TOPIC_COMMAND_ROLL}: {message}")
                # Logica Buzzer (Finta Temperatura)
                elif name == "buzzer":
                    fake_temp = 28.0 if (int(measure) == 1) else 20.0
                    fake_payload = json.dumps({
                        "name": "temperature",
                        "measure": fake_temp,
                        "timestamp": int(time.time())
                    })
                    target_topic = "esp/temperature"
                    mqtt_client.publish(target_topic, fake_payload)
                    print(f"Buzzer Command -> Spoofing Temp: {fake_payload}")
                
            except json.JSONDecodeError:
                print("Error decoding JSON from WebSocket.")
                
    except websockets.exceptions.ConnectionClosedOK:
        pass
    finally:
        CONNECTED_WEBSOCKETS.remove(websocket)
        print(f"WS client disconnected. Total: {len(CONNECTED_WEBSOCKETS)}")

# --- Funzioni MQTT ---

def on_connect(client, userdata, flags, reason_code, *args):
    """Callback connessione MQTT."""
    print("MQTT Connected. Subscribing to sensor topics.")
    for topic in MQTT_TOPIC_SENSORS:
        client.subscribe(topic)
        print(f"Subscribed to {topic}")

def on_message(client, userdata, msg):
    """Callback ricezione messaggio MQTT."""
    payload = msg.payload.decode("utf-8")
    try:
        # 1. Log sul DB
        data = json.loads(payload)
        db.log_data(data.get('timestamp'), data.get('name'), data.get('measure'))
    except Exception as e:
        print(f"Errore logging MQTT: {e}")

    # 2. Inoltro a WebSocket
    asyncio.run(send_to_all_websockets(payload))

# --- Setup MQTT ---

mqtt_client = mqtt.Client()
mqtt_client.on_connect = on_connect
mqtt_client.on_message = on_message

def run_mqtt_client():
    """Loop MQTT in thread separato."""
    try:
        mqtt_client.tls_set() 
        if MQTT_USER and MQTT_PASS:
            mqtt_client.username_pw_set(MQTT_USER, MQTT_PASS)
        
        mqtt_client.connect(MQTT_URL, MQTT_PORT, 60)
        mqtt_client.loop_forever()
    except Exception as e:
        print(f"MQTT Client Error: {e}")
        traceback.print_exc()

# --- Avvio Worker ---

async def main():
    """Loop Asyncio principale."""
    print(f"WebSocket server starting at ws://{WEBSOCKET_HOST}:{WEBSOCKET_PORT}")
    async with websockets.serve(websocket_handler, WEBSOCKET_HOST, WEBSOCKET_PORT):
        await asyncio.Future()

def run():
    """
    QUESTA è la funzione che mancava!
    Viene chiamata da app.py per avviare tutto.
    """
    print("Inizializzazione del database...")
    db.init_db()
    
    # Avvia MQTT
    mqtt_thread = threading.Thread(target=run_mqtt_client, daemon=True)
    mqtt_thread.start()
    print("MQTT Client started.")

    # Avvia WebSocket
    try:
        asyncio.run(main())
    except Exception as e:
        print(f"Errore nel worker: {e}")

if __name__ == '__main__':
    run()