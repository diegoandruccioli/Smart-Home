import sqlite3
import time
from datetime import datetime 
from variable import DB_NAME 

def get_db_connection():
    """crea una connessione al database sqlite"""
    conn = sqlite3.connect(DB_NAME)
    # imposta row factory per accedere ai dati per nome
    conn.row_factory = sqlite3.Row
    return conn

def init_db():
    """inizializza il database e crea la tabella con la colonna datetime str"""
    try:
        conn = get_db_connection()
        cursor = conn.cursor()
        
        # query che include la colonna datetime str
        cursor.execute("""
        CREATE TABLE IF NOT EXISTS sensor_data (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            timestamp INTEGER NOT NULL,
            datetime_str TEXT NOT NULL, -- colonna per data leggibile
            name TEXT NOT NULL,
            measure REAL NOT NULL 
        );
        """)
        
        conn.commit()
        conn.close()
        print(f"Database {DB_NAME}")
    except sqlite3.Error as e:
        print(f"Errore durante linizializzazione del db {e}")

def log_data(timestamp, name, measure):
    """registra un nuovo dato da sensore o comando nel database"""
    try:
        conn = get_db_connection()
        cursor = conn.cursor()
        
        # calcola la stringa datetime dal timestamp
        ts_int = int(timestamp)
        dt_string = datetime.fromtimestamp(ts_int).strftime('%Y-%m-%d %H:%M:%S')

        # inserisce tutti i valori
        cursor.execute(
            "INSERT INTO sensor_data (timestamp, datetime_str, name, measure) VALUES (?, ?, ?, ?)",
            (ts_int, dt_string, str(name), float(measure))
        )
        
        conn.commit()
        conn.close()
    except sqlite3.Error as e:
        print(f"Errore durante il logging dei dati {e}")

def get_aggregated_chart_data(sensor_name):
    """
    estrae e aggrega i dati per i grafici
    raggruppa per minuto
    """
    conn = get_db_connection()
    cursor = conn.cursor()

    # query universale
    query_template = """
    SELECT 
        -- modifica raggruppa per minuto hm invece che per ora h
        strftime('%Y-%m-%d %H:%M', timestamp, 'unixepoch') as time_bucket,
        {aggregation} as value
    FROM 
        sensor_data
    WHERE 
        name = ?
    GROUP BY 
        -- modifica raggruppa per il nuovo bucket
        time_bucket
    ORDER BY 
        time_bucket DESC
    -- modifica mostra minuti ore invece di ore
    LIMIT 180;
    """

    if sensor_name == "light":
        query = query_template.format(aggregation="AVG(measure) * 100")
    #elif sensor_name == "roll":
        #query = query_template.format(aggregation="AVG(measure)")
    else:
        query = query_template.format(aggregation="AVG(measure)")

    try:
        cursor.execute(query, (sensor_name,))
        rows = cursor.fetchall()
    except sqlite3.OperationalError:
        rows = [] # tabella vuota

    conn.close()
    
    # format per plotly
    data = {
        'x': [row['time_bucket'] for row in reversed(rows)],
        'y': [row['value'] for row in reversed(rows)]
    }
    return data