# ---
# OBIETTIVO:
# Questo script è il "Launcher" principale dell'applicazione.
# Avvia un server web Flask (per servire la dashboard e le API) e,
# contemporaneamente, lancia un processo worker separato (websocket_mqtt_worker.py)
# per gestire le connessioni in tempo reale (WebSocket e MQTT).
# ---

# Importa 'multiprocessing' per permettere l'avvio di processi separati (fondamentale per il worker)
import multiprocessing
# Importa Flask (il framework server web) e le utility per rispondere in JSON e inviare file
from flask import Flask, jsonify, send_from_directory
# Importa il tuo gestore del database (per le API dei grafici)
import database_manager as db 
# Importa 'os' per gestire i percorsi dei file (file paths)
import os

# NON importare websocket_mqtt_worker qui in alto (a livello globale).
# Questo è FONDAMENTALE. Se lo importi qui, 'multiprocessing' e il reloader
# di Flask andranno in conflitto, cercando di avviare il worker due volte o
# causando errori di "loop asyncio già in esecuzione".

def start_worker():
    """
    Questa funzione definisce il compito che il nuovo processo deve eseguire.
    Viene chiamata da 'multiprocessing.Process'.
    """
    
    # L'IMPORTAZIONE DEVE STARE QUI.
    # L'importazione avviene *all'interno* del nuovo processo,
    # garantendo che il codice del worker venga caricato solo una volta.
    import websocket_mqtt_worker 
    
    # Log per confermare l'avvio del processo worker
    print("Avvio del processo worker (MQTT/WebSocket)...")
    
    # Avvia l'esecuzione del worker (che avvierà il server WebSocket e il client MQTT)
    websocket_mqtt_worker.run()

# Inizializza l'applicazione web Flask
app = Flask(__name__)

# --- Definizione dei Percorsi Statici ---

# Calcola il percorso assoluto della cartella 'roomDashboard'
# os.path.dirname(__file__) -> ottiene la cartella di 'app.py' (cioè 'serverBridge')
# os.path.join(..., '..') -> torna indietro di un livello (alla radice 'Smart-Home')
# os.path.join(..., 'roomDashboard') -> punta alla cartella della dashboard
dashboard_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', 'roomDashboard'))


# --- API Endpoints (per i dati dei grafici) ---

# Definisce una route API. L'URL sarà /api/get_chart_data/qualsiasicosa
# <sensor_name> è una variabile dinamica presa dall'URL
@app.route('/api/get_chart_data/<sensor_name>')
def get_chart_data(sensor_name):
    """
    Endpoint API per fornire i dati aggregati per i grafici.
    Viene chiamato da 'charts.js' al caricamento della pagina.
    """
    try:
        # Controlla quale sensore è stato richiesto nell'URL
        if sensor_name == "light":
            # Chiama la funzione nel database_manager per ottenere i dati aggregati della luce
            data = db.get_aggregated_chart_data("light")
        elif sensor_name == "roll":
            # Chiama la funzione per i dati della tapparella
            data = db.get_aggregated_chart_data("roll")
        else:
            # Fallback generico se viene richiesto un altro sensore (es. "pir_sensor")
            data = db.get_aggregated_chart_data(sensor_name)
            
        # Converte il dizionario Python 'data' in una risposta JSON valida per il browser
        return jsonify(data)
    
    except Exception as e:
        # Se qualcosa va storto (es. il DB non risponde), logga l'errore nel terminale
        print(f"Errore API get_chart_data: {e}")
        # E invia una risposta di errore JSON al browser (con codice HTTP 500)
        return jsonify({"error": str(e)}), 500


# --- Gestione dei File Statici (HTML/CSS/JS) ---

# Definisce la route per la radice del sito (http://localhost:8000/)
@app.route('/')
def serve_index():
    """Serve il file index.html della dashboard."""
    # Dice a Flask di inviare il file 'index.html' dalla cartella 'dashboard_dir'
    return send_from_directory(dashboard_dir, 'index.html')

# Definisce una route "jolly" che cattura qualsiasi altro percorso
# (es. /css/style.css, /js/socket.js)
@app.route('/<path:path>')
def serve_static_files(path):
    """Serve gli asset statici (js, css, ecc.)."""
    # 'path' conterrà "css/style.css" o "js/socket.js"
    # Dice a Flask di inviare quel file specifico dalla 'dashboard_dir'
    return send_from_directory(dashboard_dir, path)


# --- Blocco di Avvio Principale ---

# Questo codice viene eseguito SOLO se avvii lo script con 'python app.py'
if __name__ == '__main__':
    
    # Questo check è FONDAMENTALE quando usi 'debug=True' e 'multiprocessing'.
    # La modalità debug avvia due processi: il "reloader" (che monitora i file)
    # e il "worker" (che esegue l'app).
    # Questa variabile d'ambiente è 'True' solo nel processo "worker",
    # impedendo al "reloader" di avviare un secondo worker per errore.
    if os.environ.get("WERKZEUG_RUN_MAIN") == "true":
        
        # Prepara il processo del worker
        # target=start_worker -> dice al processo quale funzione eseguire
        # daemon=True -> assicura che il processo worker venga chiuso automaticamente
        #                quando termini l'app Flask principale (Ctrl+C)
        worker_process = multiprocessing.Process(target=start_worker, daemon=True)
        
        # Avvia il processo worker (ora 'start_worker()' è in esecuzione)
        worker_process.start()
        
        # Logga il PID (Process ID) del worker per il debug
        print(f"Processo worker (MQTT/WS) avviato con PID: {worker_process.pid}")

    # Avvia l'applicazione Flask principale
    print(f"Server Flask (Dashboard e API) avviato su http://localhost:8000")
    
    # Avvia il server web sulla porta 8000
    # debug=True -> Abilita il ricaricamento automatico quando modifichi questo file
    app.run(debug=True, port=8000)