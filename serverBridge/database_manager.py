# ---
# OBIETTIVO:
# Questo modulo gestisce TUTTE le interazioni con il database SQLite.
# Fornisce funzioni per inizializzare il DB, scrivere nuovi dati (logging),
# e leggere/aggregare i dati storici (per le API dei grafici).
# ---

# Importa la libreria 'sqlite3', il driver Python nativo per i database SQLite
import sqlite3
# Importa 'time' (anche se non usato direttamente qui, è correlato ai timestamp)
import time
# Importa il nome del database (es. "Smart-Home/smart_home.db") dal file di configurazione
from variable import DB_NAME 

def get_db_connection():
    """Crea una connessione al database SQLite."""
    # Si connette al file specificato in DB_NAME
    conn = sqlite3.connect(DB_NAME)
    # IMPOSTAZIONE IMPORTANTE:
    # Fa sì che le righe restituite dal DB siano accessibili per nome (come un dizionario, es. row['name'])
    # invece che solo per indice (es. row[2]). Rende il codice molto più leggibile.
    conn.row_factory = sqlite3.Row
    # Restituisce l'oggetto connessione
    return conn

def init_db():
    """Inizializza il database e crea la tabella se non esiste."""
    try:
        # Apre la connessione
        conn = get_db_connection()
        # Crea un "cursore", l'oggetto che esegue materialmente le query
        cursor = conn.cursor()
        
        # Esegue una query SQL per creare la tabella
        # 'CREATE TABLE IF NOT EXISTS' è fondamentale:
        # se la tabella esiste già, non fa nulla (non cancella i dati).
        cursor.execute("""
        CREATE TABLE IF NOT EXISTS sensor_data (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            timestamp INTEGER NOT NULL,
            name TEXT NOT NULL,
            measure REAL NOT NULL 
        );
        """)
        # NOTA: Qui manca la colonna 'datetime_str' che abbiamo aggiunto dopo.
        # Questa è la versione originale del tuo codice.
        
        # Salva permanentemente le modifiche (la creazione della tabella)
        conn.commit()
        # Chiude la connessione
        conn.close()
        # Stampa un messaggio di successo nel terminale
        print(f"Database {DB_NAME} inizializzato con successo.")
    except sqlite3.Error as e:
        # Se qualcosa va storto (es. permessi di scrittura mancanti), stampa l'errore
        print(f"Errore durante l'inizializzazione del DB: {e}")

def log_data(timestamp, name, measure):
    """Registra un nuovo dato (da sensore o comando manuale) nel database."""
    try:
        # Apre una nuova connessione
        conn = get_db_connection()
        # Crea un cursore
        cursor = conn.cursor()
        
        # Esegue la query di INSERIMENTO
        # Usa i '?' (placeholder) per inserire i dati in modo sicuro
        # Questo previene errori e attacchi (SQL Injection)
        cursor.execute(
            "INSERT INTO sensor_data (timestamp, name, measure) VALUES (?, ?, ?)",
            # Passa una tupla di valori che sostituiranno i '?'
            # Fa un "casting" (conversione) per assicurarsi che i tipi siano corretti
            (int(timestamp), str(name), float(measure))
        )
        
        # Salva la nuova riga nel database
        conn.commit()
        # Chiude la connessione
        conn.close()
    except sqlite3.Error as e:
        # Se l'inserimento fallisce (es. DB bloccato), stampa l'errore
        print(f"Errore durante il logging dei dati: {e}")

# (Commento saltato)

def get_aggregated_chart_data(sensor_name):
    """
    Estrae e aggrega i dati per i grafici.
    Per 'light', calcola la % di tempo "ON" (media di 0 e 1 * 100).
    Per 'roll', calcola la media della posizione (0-100).
    """
    # Apre la connessione
    conn = get_db_connection()
    # Crea il cursore
    cursor = conn.cursor()

    # Query universale (un modello/template)
    # Definiamo la struttura della query, ma lasciamo l'{aggregation} variabile
    query_template = """
    SELECT 
        -- strftime è una funzione SQLite potentissima.
        -- Prende il 'timestamp' (formato UNIX, es. 1731500000)
        -- e lo formatta come 'ANNO-MESE-GIORNO ORA:00' (es. '2025-11-13 14:00')
        -- 'as hour_bucket' rinomina la colonna
        strftime('%Y-%m-%d %H:00', timestamp, 'unixepoch') as hour_bucket,
        
        -- Questo è un segnaposto che riempiremo (sostituito da .format())
        {aggregation} as value
    FROM 
        sensor_data
    WHERE 
        -- Seleziona solo le righe per il sensore richiesto (es. 'light' o 'roll')
        name = ?
    GROUP BY 
        -- Raggruppa tutte le righe che cadono nello STESSO 'hour_bucket'
        hour_bucket
    ORDER BY 
        -- Ordina i risultati dall'ora più recente (DESC = decrescente)
        hour_bucket DESC
    LIMIT 48; -- Prende solo le ultime 48 ore di dati
    """

    # --- Logica di Aggregazione Dinamica ---
    if sensor_name == "light":
        # Se il sensore è 'light' (valori 0 o 1):
        # Calcola la MEDIA (AVG) dei valori (es. [1, 1, 0, 0] -> media 0.5)
        # Moltiplica per 100 per ottenere la percentuale (0.5 -> 50%)
        query = query_template.format(aggregation="AVG(measure) * 100")
        
    elif sensor_name == "roll":
        # Se il sensore è 'roll' (valori 0-100):
        # Calcola semplicemente la MEDIA (AVG) della posizione (es. [100, 50, 0] -> media 50)
        query = query_template.format(aggregation="AVG(measure)")
        
    else:
        # Per qualsiasi altro sensore (es. 'pir_sensor')
        # Fa una media semplice
        query = query_template.format(aggregation="AVG(measure)")

    try:
        # Esegue la query finale, passando il nome del sensore per il 'WHERE name = ?'
        cursor.execute(query, (sensor_name,))
        # Recupera TUTTE le righe risultanti (es. le ultime 48 ore)
        rows = cursor.fetchall()
        
    except sqlite3.OperationalError as e:
        # Questo errore capita se la tabella è completamente vuota (AVG fallisce)
        print(f"Errore durante l'esecuzione della query (probabilmente tabella vuota): {e}")
        rows = [] # Restituisce una lista vuota per non far crashare l'API

    # Chiude la connessione
    conn.close()
    
    # --- Formattazione per i Grafici (Plotly) ---
    
    # Crea il dizionario che il frontend (charts.js) si aspetta
    data = {
        # 'reversed(rows)' -> I dati sono DESC (dal più nuovo al più vecchio)
        # Il grafico li vuole dal più vecchio al più nuovo (da sx a dx)
        # quindi invertiamo la lista.
        
        # Crea una lista di tutte le etichette 'hour_bucket' (es. ['2025-11-13 13:00', ...])
        'x': [row['hour_bucket'] for row in reversed(rows)],
        # Crea una lista di tutti i 'value' calcolati (es. [50, 75, ...])
        'y': [row['value'] for row in reversed(rows)]
    }
    # Restituisce i dati formattati all'API (app.py)
    return data