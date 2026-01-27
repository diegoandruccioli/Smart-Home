# launcher principale dell'applicazione
# avvia un server web flask per servire la dashboard e le api e
# contemporaneamente lancia un processo worker separato websocket mqtt worker py
# per gestire le connessioni in tempo reale websocket e mqtt

# importa multiprocessing per permettere avvio di processi separati (per il worker)
import multiprocessing
# importa flask il framework server web e le utility per rispondere in json e inviare file
from flask import Flask, jsonify, send_from_directory
# importa il gestore del database per le api dei grafici
import database_manager as db 
# importa os per gestire i percorsi dei file paths
import os

def start_worker():
    """
    questa funzione definisce il compito che il nuovo processo deve eseguire
    viene chiamata da multiprocessing process
    """
    
    import websocket_mqtt_worker 
    
    # log per confermare lavvio del processo worker
    print("Avvio del processo worker (MQTT/WebSocket)...")
    
    # avvia lesecuzione del worker che avvierà il server websocket e il client mqtt
    websocket_mqtt_worker.run()

# inizializza lapplicazione web flask
app = Flask(__name__)

# definizione dei percorsi statici

# calcola il percorso assoluto della cartella roomdashboard
# os path dirname file ottiene la cartella di app py cioè serverbridge
# os path join torna indietro di un livello alla radice smart home
# os path join punta alla cartella della dashboard
dashboard_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', 'roomDashboard'))


# api endpoints per i dati dei grafici

# definisce una route api, l'url sarà /api/get_chart_data/...
# sensor name è una variabile dinamica presa dall'url
@app.route('/api/get_chart_data/<sensor_name>')
def get_chart_data(sensor_name):
    """
    endpoint api per fornire i dati aggregati per i grafici
    viene chiamato da charts js al caricamento della pagina
    """
    try:
        # controlla quale sensore è stato richiesto nell'url
        if sensor_name == "light":
            # chiama la funzione nel database manager per ottenere i dati aggregati della luce
            data = db.get_aggregated_chart_data("light")
        #elif sensor_name == "roll":
            # chiama la funzione per i dati della tapparella
            #data = db.get_aggregated_chart_data("roll")
        else:
            # fallback generico se viene richiesto un altro sensore es pir sensor
            data = db.get_aggregated_chart_data(sensor_name)
            
        # converte il dizionario python data in una risposta json valida per il browser
        return jsonify(data)
    
    except Exception as e:
        # se qualcosa va storto es il db non risponde logga lerrore nel terminale
        print(f"Errore API get_chart_data: {e}")
        # e invia una risposta di errore json al browser con codice http
        return jsonify({"error": str(e)}), 500


# gestione dei file statici html,css,js

# definisce la route principale root dell'applicazione
@app.route('/')
def serve_index():
    """serve il file index html della dashboard"""
    # dice a flask di inviare il file index html dalla cartella dashboard dir
    return send_from_directory(dashboard_dir, 'index.html')

# definisce una route jolly che cattura qualsiasi altro percorso
@app.route('/<path:path>')
def serve_static_files(path):
    """serve gli asset statici js css ecc"""
    # path contiene css, style.css o js, socket.js
    # dice a flask di inviare quel file specifico dalla dashboard dir
    return send_from_directory(dashboard_dir, path)


# blocco di avvio principale

# questo codice viene eseguito solo se avvii lo script con python app py
if __name__ == '__main__':
    
    # questo check è fondamentale quando si usa debug true e multiprocessing
    # la modalità debug avvia due processi: il reloader che monitora i file
    # e il worker che esegue l'app
    # questa variabile d ambiente è true solo nel processo worker
    # impedendo al reloader di avviare un secondo worker per errore
    if os.environ.get("WERKZEUG_RUN_MAIN") == "true":
        
        # prepara il processo del worker
        # target=start_worker dice al processo quale funzione eseguire
        # daemon true assicura che il processo worker venga chiuso automaticamente
        worker_process = multiprocessing.Process(target=start_worker, daemon=True)
        
        # avvia il processo worker ora start_worker è in esecuzione
        worker_process.start()
        
        # logga il pid process id del worker per il debug
        print(f"Processo worker (MQTT/WS) avviato con PID: {worker_process.pid}")

    # avvia l'applicazione flask principale
    print(f"Server Flask (Dashboard e API) avviato su http localhost")
    
    
    app.run(debug=True, port=8000)
