# FILE: serverBridge/app.py

import multiprocessing
from flask import Flask, jsonify, send_from_directory
import database_manager as db 
import os
# NON importare websocket_mqtt_worker qui in alto

def start_worker():
    """Questa funzione avvia il processo worker."""
    # L'IMPORTAZIONE DEVE STARE QUI
    import websocket_mqtt_worker 
    print("Avvio del processo worker (MQTT/WebSocket)...")
    websocket_mqtt_worker.run()

app = Flask(__name__)

# Ottieni il percorso assoluto della cartella 'roomDashboard'
dashboard_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', 'roomDashboard'))

# --- API Endpoints ---
@app.route('/api/get_chart_data/<sensor_name>')
def get_chart_data(sensor_name):
    """
    Endpoint API per fornire i dati aggregati per i grafici.
    """
    try:
        if sensor_name == "light":
            data = db.get_aggregated_chart_data("light")
        elif sensor_name == "roll":
            data = db.get_aggregated_chart_data("roll")
        else:
            data = db.get_aggregated_chart_data(sensor_name)
            
        return jsonify(data)
    except Exception as e:
        print(f"Errore API get_chart_data: {e}")
        return jsonify({"error": str(e)}), 500

# --- Serve l'interfaccia ---
@app.route('/')
def serve_index():
    """Serve il file index.html della dashboard."""
    return send_from_directory(dashboard_dir, 'index.html')

@app.route('/<path:path>')
def serve_static_files(path):
    """Serve gli asset statici (js, css)."""
    return send_from_directory(dashboard_dir, path)


if __name__ == '__main__':
    # Questo check assicura che il worker sia avviato una sola volta
    if os.environ.get("WERKZEUG_RUN_MAIN") == "true":
        
        worker_process = multiprocessing.Process(target=start_worker, daemon=True)
        worker_process.start()
        print(f"Processo worker (MQTT/WS) avviato con PID: {worker_process.pid}")

    # Avvia l'applicazione Flask (che serve l'index.html e l'API)
    print(f"Server Flask (Dashboard e API) avviato su http://localhost:8000")
    app.run(debug=True, port=8000)