# ---
# OBIETTIVO:
# Questo è il "Worker Process" dell'applicazione. È un processo separato
# (avviato da app.py) che gestisce TUTTE le comunicazioni in tempo reale.
#
# FA TRE COSE CONTEMPORANEAMENTE:
# 1. ASCOLTA i comandi dalla Dashboard (tramite WebSocket sulla porta 8080).
# 2. ASCOLTA i dati dai sensori ESP32 (tramite MQTT).
# 3. REGISTRA tutto nel database (tramite database_manager).
# ---

# Importa la libreria 'paho-mqtt' per connettersi al broker MQTT
import paho.mqtt.client as mqtt
# Importa 'json' per convertire stringhe (testo) in oggetti Python e viceversa
import json
# Importa 'asyncio' per la programmazione asincrona (necessario per i WebSocket)
import asyncio
# Importa la libreria 'websockets' per creare il server WebSocket
import websockets
# Importa 'threading' per permettere a MQTT di girare in un thread separato
# (senza bloccare asyncio)
import threading
# Importa 'time' per ottenere il timestamp attuale del server (per i comandi manuali)
import time 
# Importa TUTTE le costanti (URL, porte, topic) dal file di configurazione
from variable import *
# Importa le funzioni del database (init_db, log_data)
import database_manager as db
# Importa 'traceback' per stampare errori dettagliati nel terminale (debug)
import traceback

# --- Gestione Client WebSocket ---

# Un 'set' (elenco) globale che tiene traccia di tutti i browser (dashboard)
# attualmente connessi al server WebSocket.
CONNECTED_WEBSOCKETS = set()

async def send_to_all_websockets(message):
    """Invia un messaggio a tutti i client WebSocket connessi."""
    
    # Se l'elenco non è vuoto (c'è almeno un utente connesso)
    if CONNECTED_WEBSOCKETS:
        # Prepara un elenco di "compiti di invio" (uno per ogni utente)
        send_tasks = [ws.send(message) for ws in CONNECTED_WEBSOCKETS]
        
        # Esegue tutti i compiti di invio contemporaneamente (in parallelo)
        # 'return_exceptions=True' evita che un singolo utente disconnesso
        # faccia crashare l'intero server.
        await asyncio.gather(*send_tasks, return_exceptions=True)
        # (Debug disabilitato)
        # print(f"Message forwarded to {len(CONNECTED_WEBSOCKETS)} WebSocket clients.")

async def websocket_handler(websocket):
    """
    Gestisce un singolo client WebSocket. 
    Questa funzione viene chiamata AUTOMATICAMENTE ogni volta che
    una nuova dashboard si connette al server (porta 8080).
    """
    
    # Aggiunge il nuovo utente/dashboard all'elenco globale
    CONNECTED_WEBSOCKETS.add(websocket)
    print(f"WS client connected. Total: {len(CONNECTED_WEBSOCKETS)}")
    
    try:
        # 'async for' attende (senza bloccare) che arrivi un messaggio da QUESTA dashboard
        async for message in websocket:
            # Messaggio ricevuto dalla Dashboard (Comando manuale)
            print(f"WS Command received: {message}")
            
            try:
                # Converte il messaggio (stringa JSON) in un oggetto Python
                data = json.loads(message)
                # Estrae 'name' (es. "light", "roll")
                name = data.get('name')
                # Estrae 'measure' (es. 1, 0, "50")
                measure = data.get('measure')
                
                # --- LOGICA DI BUSINESS (WS) ---
                
                # 1. Log sul DB: Salva il comando manuale nel database
                # Usa 'time.time()' perché il comando è generato ORA dal server
                db.log_data(int(time.time()), name, measure)

                # 2. Inoltro a MQTT: Inoltra il comando ai dispositivi ESP32
                
                # Se è un comando per la luce...
                if name in ["light", "manual_light"]:
                    # ...pubblica il messaggio sul topic dei comandi luce
                    mqtt_client.publish(MQTT_TOPIC_COMMAND_LIGHT, message)
                    print(f"Published to {MQTT_TOPIC_COMMAND_LIGHT}: {message}")
                    
                # Se è un comando per la tapparella...
                elif name in ["roll", "manual_roll"]:
                    # ...pubblica il messaggio sul topic dei comandi tapparella
                    mqtt_client.publish(MQTT_TOPIC_COMMAND_ROLL, message)
                    print(f"Published to {MQTT_TOPIC_COMMAND_ROLL}: {message}")
                
            except json.JSONDecodeError:
                # Se il messaggio ricevuto dal web non è un JSON valido
                print("Error decoding JSON from WebSocket.")
                
    except websockets.exceptions.ConnectionClosedOK:
        # L'utente ha chiuso la pagina web (normale amministrazione)
        pass
    finally:
        # Blocco 'finally': viene eseguito SEMPRE (sia se l'utente chiude, sia in caso di errore)
        # Rimuove l'utente dall'elenco globale
        CONNECTED_WEBSOCKETS.remove(websocket)
        print(f"WS client disconnected. Total: {len(CONNECTED_WEBSOCKETS)}")

# --- Funzioni MQTT ---

# Definisce la funzione 'on_connect' (callback)
# Verrà chiamata AUTOMATICAMENTE quando il client MQTT si connette al broker
# Gli *args servono per compatibilità (catturano argomenti extra)
def on_connect(client, userdata, flags, reason_code, *args):
    """Callback chiamata alla connessione MQTT."""
    print("MQTT Connected. Subscribing to sensor topics.")
    
    # Iscriviti a tutti i topic dei sensori definiti in 'variable.py'
    for topic in MQTT_TOPIC_SENSORS:
        client.subscribe(topic)
        print(f"Subscribed to {topic}")

# Definisce la funzione 'on_message' (callback)
# Verrà chiamata AUTOMATICAMENTE ogni volta che arriva un messaggio
# da un topic a cui siamo iscritti
def on_message(client, userdata, msg):
    """Callback chiamata alla ricezione di un messaggio MQTT (Dati Sensori)."""
    
    # Converte il payload (byte) in una stringa di testo (utf-8)
    payload = msg.payload.decode("utf-8")
    # (Debug disabilitato)
    # print(f"MQTT Data received ({msg.topic}): {payload}")

    try:
        # --- LOGICA DI BUSINESS (MQTT) ---
        
        # 1. Log sul DB: Salva i dati del sensore nel database
        data = json.loads(payload)
        # Usa il timestamp e i dati generati DIRETTAMENTE dall'ESP32
        db.log_data(data.get('timestamp'), data.get('name'), data.get('measure'))
        
    except json.JSONDecodeError:
        print("Errore nel payload MQTT, non è JSON valido.")
    except Exception as e:
        print(f"Errore during il logging MQTT: {e}")

    # 2. Inoltro a WebSocket: Inoltra i dati del sensore a TUTTE le dashboard connesse
    
    # 'asyncio.run()' è FONDAMENTALE.
    # Siamo in un thread normale (MQTT), ma 'send_to_all_websockets' è
    # una funzione asincrona (async). 'asyncio.run()' crea un mini-loop
    # temporaneo per "lanciare" la funzione asincrona da un contesto sincrono.
    asyncio.run(send_to_all_websockets(payload))


# --- Inizializzazione Client MQTT ---

# Crea l'oggetto client MQTT (usando la sintassi deprecata V1)
mqtt_client = mqtt.Client()
# Associa la funzione 'on_connect' all'evento "connessione"
mqtt_client.on_connect = on_connect
# Associa la funzione 'on_message' all'evento "messaggio ricevuto"
mqtt_client.on_message = on_message

def run_mqtt_client():
    """Connessione e loop MQTT in un thread separato."""
    try:
        # Abilita la sicurezza TLS/SSL (necessaria per la porta 8883 di HiveMQ)
        mqtt_client.tls_set() 
        
        # Controlla se le credenziali sono state impostate in 'variable.py'
        if MQTT_USER and MQTT_PASS:
            # Imposta username e password per l'autenticazione
            mqtt_client.username_pw_set(MQTT_USER, MQTT_PASS)
            print(f"MQTT: Trovate credenziali, connessione con utente: {MQTT_USER}")
        else:
            # Avvisa se le credenziali mancano
            print("MQTT: Attenzione, utente/password non impostati in variable.py. Connessione anonima.")
        
        # Tenta la connessione al broker (URL e Porta da 'variable.py')
        mqtt_client.connect(MQTT_URL, MQTT_PORT, 60)
        
        # 'loop_forever()' è un loop BLOCCANTE.
        # Tiene questo thread vivo e in ascolto per sempre (finché il processo non muore).
        mqtt_client.loop_forever()
        
    except Exception as e:
        # Se la connessione fallisce (es. 'timed out')
        print(f"MQTT Client Error: {e}")
        traceback.print_exc() # Stampa l'errore dettagliato

# --- Funzioni di Avvio Worker (Asyncio) ---

async def main():
    """Funzione asincrona principale per avviare il server WebSocket."""
    print(f"WebSocket server starting at ws://{WEBSOCKET_HOST}:{WEBSOCKET_PORT}")
    
    # 'async with websockets.serve(...)' avvia il server WebSocket
    # e lo tiene attivo finché il blocco 'with' non finisce
    async with websockets.serve(websocket_handler, WEBSOCKET_HOST, WEBSOCKET_PORT):
        # Il server è in esecuzione.
        # 'await asyncio.Future()' è un trucco per "dormire" all'infinito
        # (senza bloccare il loop), tenendo vivo il blocco 'with' per sempre.
        await asyncio.Future()

def run():
    """
    Avvia il bridge completo.
    Questa è la funzione chiamata da 'app.py' quando avvia il processo.
    """
    
    # 1. Inizializza il DB (sincrono)
    print("Inizializzazione del database...")
    db.init_db()
    
    # 2. Avvia il client MQTT (in un thread separato)
    # Prepara il thread, dicendogli di eseguire la funzione 'run_mqtt_client'
    # 'daemon=True' assicura che questo thread muoia quando muore il processo principale
    mqtt_thread = threading.Thread(target=run_mqtt_client, daemon=True)
    # Avvia il thread. Ora 'run_mqtt_client' sta girando in background.
    mqtt_thread.start()
    print("MQTT Client started in background thread.")

    # 3. Avvia il server WebSocket (nel thread principale)
    try:
        # 'asyncio.run(main())' è il modo moderno per avviare
        # un'applicazione asyncio. Crea il loop, esegue 'main'
        # (che a sua volta avvia il server e "dorme"), e gestisce tutto.
        # Questa chiamata è BLOCCANTE (non uscirà finché il server non crasha).
        asyncio.run(main())
        
    except RuntimeError as e:
        # Gestisce gli errori di avvio di asyncio
        print(f"--- ERRORE RUNTIME ASYNCIO ---")
        print(f"Messaggio: {e}")
        traceback.print_exc()
        print(f"---------------------------------")
        
    except OSError as e:
        # Gestisce errori del Sistema Operativo
        if e.errno == 10048: # Address already in use
             print(f"ERRORE: La porta {WEBSOCKET_PORT} è già in uso. Chiudi altri processi.")
        else:
             print(f"Errore OS: {e}")
             traceback.print_exc()
    
    except Exception as e:
        # Cattura qualsiasi altro errore
        print(f"--- ERRORE GENERICO NEL WORKER ---")
        print(f"Messaggio: {e}")
        traceback.print_exc()
        print(f"----------------------------------")

# Blocco standard Python
# Se esegui questo file DIRETTAMENTE (es. 'python websocket_mqtt_worker.py')
# (Cosa che NON dovresti fare, perché va avviato da app.py)
if __name__ == '__main__':
    # ...esegue la funzione 'run()'
    run()