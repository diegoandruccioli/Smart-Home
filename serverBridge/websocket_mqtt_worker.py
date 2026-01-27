# worker process con logica bridge
# gestore del conflitto tra sensore reale e comandi manuali

import paho.mqtt.client as mqtt
import json
import asyncio
import websockets
import threading
import time 
from variable import *
import database_manager as db
import traceback

# false  automatico sensore comanda
# true  manuale utente comanda sensore ignorato
SYSTEM_IS_MANUAL = False 

# gestione client websocket
CONNECTED_WEBSOCKETS = set()

async def send_to_all_websockets(message):
    """invia un messaggio a tutti i client websocket connessi"""
    if CONNECTED_WEBSOCKETS:
        send_tasks = [ws.send(message) for ws in CONNECTED_WEBSOCKETS]
        await asyncio.gather(*send_tasks, return_exceptions=True)

async def websocket_handler(websocket):
    """gestisce i comandi dalla dashboard"""
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
                
                # log sul db
                db.log_data(int(time.time()), name, measure)

                # rilevamento comando manuale
                if name == "manual_light":
                    # manuale attivo automatico
                    SYSTEM_IS_MANUAL = (int(measure) == 1)
                    print(f"--- SYSTEM MANUAL MODE CHANGED: {SYSTEM_IS_MANUAL} ---")
                    
                    # inoltra comunque il comando allattuatore per attivarediattivare logica led locale
                    mqtt_client.publish(MQTT_TOPIC_COMMAND_LIGHT, message)

                #
                elif name == "light":
                    mqtt_client.publish(MQTT_TOPIC_COMMAND_LIGHT, message)
                
                #elif name in roll manual roll
                #    mqtt_client.publish(MQTT_TOPIC_COMMAND_ROLL, message)

                # logica buzzer in manuale
                elif name == "buzzer":
                    # spoofing inviamo una temperatura finta per attivare il buzzer dellattuatore
                    fake_temp = 28.0 if (int(measure) == 1) else 20.0
                    fake_payload = json.dumps({
                        "name": "temperature",
                        "measure": fake_temp,
                        "timestamp": int(time.time())
                    })
                    # inviamo al topic che lattuatore ascolta esptemperature
                    mqtt_client.publish("esp/temperature", fake_payload)
                    print(f"Manual Buzzer -> Spoofing to Actuator: {fake_temp}°C")
                
            except json.JSONDecodeError:
                print("Error decoding JSON from WebSocket.")
                
    except websockets.exceptions.ConnectionClosedOK:
        pass
    finally:
        CONNECTED_WEBSOCKETS.remove(websocket)
        print(f"WS Disconnect. Total: {len(CONNECTED_WEBSOCKETS)}")


def on_connect(client, userdata, flags, reason_code, *args):
    print("MQTT Connected.")
    for topic in MQTT_TOPIC_SENSORS:
        client.subscribe(topic)
        print(f"Subscribed to {topic}")

def on_message(client, userdata, msg):
    payload = msg.payload.decode("utf-8")
    topic = msg.topic
    
    try:
        data = json.loads(payload)
        name = data.get('name')
        
        # log sempre tutto sul db storico completo
        db.log_data(data.get('timestamp'), name, data.get('measure'))

        # logica bridge inoltro intelligente
        
        # caso a messaggio dal sensore fisico sensor
        if "sensor/" in topic:
            if not SYSTEM_IS_MANUAL:
                # se siamo in automatico
                # inoltra il dato allattuatore cambia topic da sensor a esp
                target_topic = topic.replace("sensor/", "esp/")
                client.publish(target_topic, payload)
                
                # invia anche alla dashboard per aggiornare il grafico
                asyncio.run(send_to_all_websockets(payload))
            else:
                # se siamo in manuale
                # blocca tutto non mandare allattuatore così non sovrascrive il buzzer
                # non mandare alla dashboard così non flickera il grafico
                pass 

        # caso b messaggio dallattuatore o comando manuale esp
        else:
            # se arriva un messaggio su esp es la nostra temperatura finta o feedback led
            # mandalo alla dashboard così lutente vede che il comando è stato preso
            asyncio.run(send_to_all_websockets(payload))

    except Exception as e:
        print(f"MQTT Error: {e}")

# setup standard

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