# FILE: server_bridge/app.py

import multiprocessing
from flask import Flask
from views import views
import os

def start_worker():
    # Importa il nuovo worker
    import websocket_mqtt_worker 
    websocket_mqtt_worker.run()

app = Flask(__name__)
# Assicurati che il file views.py sia presente nella stessa directory o nel path di sistema
# app.register_blueprint(views, url_prefix="/") 

if __name__ == '__main__':
    # Questo check assicura che il worker sia avviato una sola volta (Flask lo avvia due volte in debug)
    if os.environ.get("WERKZEUG_RUN_MAIN") == "true":
        worker_process = multiprocessing.Process(target=start_worker)
        worker_process.start()
        print(f"MQTT/WS Bridge process started with PID: {worker_process.pid}")

    try:
        # Avvia l'applicazione Flask (che serve l'index.html)
        app.run(debug=True, port=8000) 
    finally:
        if os.environ.get("WERKZEUG_RUN_MAIN") == "true":
            worker_process.terminate()
            print("MQTT/WS Bridge process terminated.")