# FILE: serverBridge/database_manager.py

import sqlite3
import time
from datetime import datetime # <-- Importa datetime
from variable import DB_NAME 

def get_db_connection():
    """Crea una connessione al database SQLite."""
    conn = sqlite3.connect(DB_NAME)
    # Imposta row_factory per accedere ai dati per nome
    conn.row_factory = sqlite3.Row
    return conn

def init_db():
    """Inizializza il database e crea la tabella con la colonna datetime_str."""
    try:
        conn = get_db_connection()
        cursor = conn.cursor()
        
        # Query che include la colonna datetime_str
        cursor.execute("""
        CREATE TABLE IF NOT EXISTS sensor_data (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            timestamp INTEGER NOT NULL,
            datetime_str TEXT NOT NULL, -- <-- Colonna per data leggibile
            name TEXT NOT NULL,
            measure REAL NOT NULL 
        );
        """)
        
        conn.commit()
        conn.close()
        print(f"Database {DB_NAME} inizializzato (con colonna datetime_str).")
    except sqlite3.Error as e:
        print(f"Errore durante l'inizializzazione del DB: {e}")

def log_data(timestamp, name, measure):
    """Registra un nuovo dato (da sensore o comando) nel database."""
    try:
        conn = get_db_connection()
        cursor = conn.cursor()
        
        # Calcola la stringa datetime dal timestamp
        ts_int = int(timestamp)
        dt_string = datetime.fromtimestamp(ts_int).strftime('%Y-%m-%d %H:%M:%S')

        # Inserisce tutti e 4 i valori
        cursor.execute(
            "INSERT INTO sensor_data (timestamp, datetime_str, name, measure) VALUES (?, ?, ?, ?)",
            (ts_int, dt_string, str(name), float(measure))
        )
        
        conn.commit()
        conn.close()
    except sqlite3.Error as e:
        print(f"Errore durante il logging dei dati: {e}")

def get_aggregated_chart_data(sensor_name):
    """
    Estrae e aggrega i dati per i grafici.
    RAGGRUPPA PER MINUTO.
    """
    conn = get_db_connection()
    cursor = conn.cursor()

    # Query universale
    query_template = """
    SELECT 
        -- MODIFICA: Raggruppa per Minuto (H:M) invece che per Ora (H:00)
        strftime('%Y-%m-%d %H:%M', timestamp, 'unixepoch') as time_bucket,
        {aggregation} as value
    FROM 
        sensor_data
    WHERE 
        name = ?
    GROUP BY 
        -- MODIFICA: Raggruppa per il nuovo bucket
        time_bucket
    ORDER BY 
        time_bucket DESC
    -- MODIFICA: Mostra 180 minuti (3 ore) invece di 48 ore
    LIMIT 180;
    """

    if sensor_name == "light":
        query = query_template.format(aggregation="AVG(measure) * 100")
    elif sensor_name == "roll":
        query = query_template.format(aggregation="AVG(measure)")
    else:
        query = query_template.format(aggregation="AVG(measure)")

    try:
        cursor.execute(query, (sensor_name,))
        rows = cursor.fetchall()
    except sqlite3.OperationalError:
        rows = [] # Tabella vuota

    conn.close()
    
    # Format per Plotly
    data = {
        'x': [row['time_bucket'] for row in reversed(rows)],
        'y': [row['value'] for row in reversed(rows)]
    }
    return data