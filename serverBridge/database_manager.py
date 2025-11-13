# FILE: serverBridge/database_manager.py
import sqlite3
import time
from variable import DB_NAME # Importeremo questo da variable.py

def get_db_connection():
    """Crea una connessione al database SQLite."""
    conn = sqlite3.connect(DB_NAME)
    conn.row_factory = sqlite3.Row
    return conn

def init_db():
    """Inizializza il database e crea la tabella se non esiste."""
    try:
        conn = get_db_connection()
        cursor = conn.cursor()
        
        # Creiamo una tabella unica per tutti i dati
        # 'name' = light, roll, pir_sensor, manual_light, etc.
        cursor.execute("""
        CREATE TABLE IF NOT EXISTS sensor_data (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            timestamp INTEGER NOT NULL,
            name TEXT NOT NULL,
            measure REAL NOT NULL 
        );
        """)
        
        conn.commit()
        conn.close()
        print(f"Database {DB_NAME} inizializzato con successo.")
    except sqlite3.Error as e:
        print(f"Errore durante l'inizializzazione del DB: {e}")

def log_data(timestamp, name, measure):
    """Registra un nuovo dato (da sensore o comando manuale) nel database."""
    try:
        conn = get_db_connection()
        cursor = conn.cursor()
        
        cursor.execute(
            "INSERT INTO sensor_data (timestamp, name, measure) VALUES (?, ?, ?)",
            (int(timestamp), str(name), float(measure))
        )
        
        conn.commit()
        conn.close()
    except sqlite3.Error as e:
        print(f"Errore durante il logging dei dati: {e}")

# Funzione per aggregare i dati per i grafici
# Questo replica la logica di aggregazione oraria vista in charts.js
def get_aggregated_chart_data(sensor_name):
    """
    Estrae e aggrega i dati per i grafici.
    Calcola la percentuale di tempo "ON" (measure=1) per ogni ora.
    """
    conn = get_db_connection()
    cursor = conn.cursor()

    # I dati dai sensori arrivano ogni secondo.
    # Contiamo i secondi in cui 'measure' era 1 e raggruppiamo per ora.
    query = """
    SELECT 
        strftime('%Y-%m-%d %H:00', timestamp, 'unixepoch') as hour_bucket,
        (COUNT(*) * 100.0 / 3600.0) as on_percentage
    FROM 
        sensor_data
    WHERE 
        name = ? AND measure = 1
    GROUP BY 
        hour_bucket
    ORDER BY 
        hour_bucket DESC
    LIMIT 48; -- Ultime 48 ore
    """
    
    cursor.execute(query, (sensor_name,))
    rows = cursor.fetchall()
    conn.close()
    
    # Format per Plotly
    data = {
        'x': [row['hour_bucket'] for row in reversed(rows)],
        'y': [row['on_percentage'] for row in reversed(rows)]
    }
    return data