# ---
# OBIETTIVO:
# Worker Process con LOGICA BRIDGE.
# Gestisce il conflitto tra Sensore Reale e Comandi Manuali.
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

# --- STATO GLOBALE DEL SISTEMA ---
# False = Automatico (Sensore comanda)
# True = Manuale (Utente comanda, Sensore ignorato)
SYSTEM_IS_MANUAL = False 

# --- Gestione Client WebSocket ---

CONNECTED_WEBSOCKETS = set()

async def send_to_all_websockets(message):
    """Invia un messaggio a tutti i client WebSocket connessi."""
    if CONNECTED_WEBSOCKETS:
        send_tasks = [ws.send(message) for ws in CONNECTED_WEBSOCKETS]
        await asyncio.gather(*send_tasks, return_exceptions=True)

async def websocket_handler(websocket):
    """Gestisce i comandi dalla Dashboard."""
    global SYSTEM_IS_MANUAL 
    
    CONNECTED_WEBSOCKETS.add(websocket)
    print(f"WS client connected. Total: {len(CONNECTED_WEBSOCKETS)}")
    
    try:
        async for message in websocket:
            print(f"WS Command: {message}")
            try:
                data = json.loads(message)
                name = data.get('name')
                measure = data.get('measure')
                
                # 1. Log sul DB
                db.log_data(int(time.time()), name, measure)

                # --- RILEVAMENTO CAMBIO MODALITÀ ---
                if name == "manual_light":
                    # 1 = Manuale Attivo, 0 = Automatico
                    SYSTEM_IS_MANUAL = (int(measure) == 1)
                    print(f"--- SYSTEM MANUAL MODE CHANGED: {SYSTEM_IS_MANUAL} ---")
                    
                    # Inoltra comunque il comando all'attuatore per attivare/disattivare logica LED locale
                    mqtt_client.publish(MQTT_TOPIC_COMMAND_LIGHT, message)

                # --- GESTIONE ALTRI COMANDI ---
                elif name == "light":
                    mqtt_client.publish(MQTT_TOPIC_COMMAND_LIGHT, message)
                
                elif name in ["roll", "manual_roll"]:
                    mqtt_client.publish(MQTT_TOPIC_COMMAND_ROLL, message)

                # --- LOGICA BUZZER (Solo se in Manuale) ---
                elif name == "buzzer":
                    # Spoofing: Inviamo una temperatura finta per attivare il buzzer dell'attuatore
                    fake_temp = 28.0 if (int(measure) == 1) else 20.0
                    fake_payload = json.dumps({
                        "name": "temperature",
                        "measure": fake_temp,
                        "timestamp": int(time.time())
                    })
                    # Inviamo al topic CHE L'ATTUATORE ASCOLTA (esp/temperature)
                    mqtt_client.publish("esp/temperature", fake_payload)
                    print(f"Manual Buzzer -> Spoofing to Actuator: {fake_temp}°C")
                
            except json.JSONDecodeError:
                print("Error decoding JSON from WebSocket.")
                
    except websockets.exceptions.ConnectionClosedOK:
        pass
    finally:
        CONNECTED_WEBSOCKETS.remove(websocket)
        print(f"WS Disconnect. Total: {len(CONNECTED_WEBSOCKETS)}")

# --- Funzioni MQTT (IL VIGILE URBANO) ---

def on_connect(client, userdata, flags, reason_code, *args):
    print("MQTT Connected.")
    for topic in MQTT_TOPIC_SENSORS:
        client.subscribe(topic)
        print(f"Subscribed to {topic}")

def on_message(client, userdata, msg):
    """
    Qui avviene il filtraggio dei dati.
    Decidiamo se inoltrare il sensore all'attuatore o no.
    """
    payload = msg.payload.decode("utf-8")
    topic = msg.topic
    
    try:
        data = json.loads(payload)
        name = data.get('name')
        
        # 1. Log sempre tutto sul DB (storico completo)
        db.log_data(data.get('timestamp'), name, data.get('measure'))

        # 2. LOGICA BRIDGE (Inoltro Intelligente)
        
        # CASO A: Messaggio dal SENSORE FISICO (sensor/...)
        if "sensor/" in topic:
            if not SYSTEM_IS_MANUAL:
                # SE SIAMO IN AUTOMATICO:
                # Inoltra il dato all'attuatore (cambia topic da sensor/ a esp/)
                target_topic = topic.replace("sensor/", "esp/")
                client.publish(target_topic, payload)
                
                # Invia anche alla Dashboard per aggiornare il grafico
                asyncio.run(send_to_all_websockets(payload))
            else:
                # SE SIAMO IN MANUALE:
                # BLOCCA TUTTO. Non mandare all'attuatore (così non sovrascrive il buzzer).
                # Non mandare alla Dashboard (così non "flickera" il grafico).
                pass 

        # CASO B: Messaggio dall'ATTUATORE o COMANDO MANUALE (esp/...)
        else:
            # Se arriva un messaggio su esp/ (es. la nostra temperatura finta o feedback led)
            # mandalo alla dashboard così l'utente vede che il comando è stato preso.
            asyncio.run(send_to_all_websockets(payload))

    except Exception as e:
        print(f"MQTT Error: {e}")

# --- Setup Standard ---

mqtt_client = mqtt.Client()
mqtt_client.on_connect = on_connect
mqtt_client.on_message = on_message

def run_mqtt_client():
    try:
        mqtt_client.tls_set() 
        if MQTT_USER and MQTT_PASS:
            mqtt_client.username_pw_set(MQTT_USER, MQTT_PASS)
        mqtt_client.connect(MQTT_URL, MQTT_PORT, 60)
        mqtt_client.loop_forever()
    except Exception as e:
        print(f"MQTT Client Error: {e}")
        traceback.print_exc()

async def main():
    print(f"WS Server running on port {WEBSOCKET_PORT}")
    async with websockets.serve(websocket_handler, WEBSOCKET_HOST, WEBSOCKET_PORT):
        await asyncio.Future()

def run():
    print("Init DB...")
    db.init_db()
    
    mqtt_thread = threading.Thread(target=run_mqtt_client, daemon=True)
    mqtt_thread.start()
    print("MQTT Client started.")
    
    try:
        asyncio.run(main())
    except Exception as e:
        print(f"Error: {e}")

if __name__ == '__main__':
    run()