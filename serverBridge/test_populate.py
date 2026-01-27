import sqlite3
import time
import os
import random
from datetime import datetime

from variable import DB_NAME 

# blocco di sicurezza
if not os.path.exists(DB_NAME):
    print(f"Errore: Database '{DB_NAME}' non trovato.")
    print("Avvia prima 'app.py' (Ctrl+C) per crearlo, poi esegui questo script.")
    exit()

now = int(time.time())
minute = 60
processed_data = [] # lista finale per linserimento

print("Generazione dati di test al minuto per le ultime 3 ore...")

# simula dati per le ultime ore minuti
for i in range(180):
    # timestamp per ogni minuto passato
    ts = now - (i * minute)
    # calcola la stringa leggibile
    dt_string = datetime.fromtimestamp(ts).strftime('%Y-%m-%d %H:%M:%S')
    
    # simula dati luce o
    if i > 60: # nelle prime ore
        light_measure = 1 if random.random() > 0.5 else 0
    else: # nellultima ora
        light_measure = 1 if random.random() > 0.1 else 0
    
    processed_data.append((ts, dt_string, "light", light_measure))
        
    # simula dati tapparella
    roll_position = max(0, min(100, (i / 1.8) * (random.uniform(0.9, 1.1))))
    processed_data.append((ts, dt_string, "roll", int(roll_position)))


try:
    conn = sqlite3.connect(DB_NAME)
    cursor = conn.cursor()
    
    print(f"Connesso a {DB_NAME}. Inserimento di {len(processed_data)} record di test...")
    
    # query di inserimento per la tabella a colonne
    cursor.executemany(
        "INSERT INTO sensor_data (timestamp, datetime_str, name, measure) VALUES (?, ?, ?, ?)",
        processed_data
    )
    
    conn.commit()
    print(f"Dati inseriti con successo. {conn.total_changes} righe modificate.")
    
except sqlite3.Error as e:
    print(f"Errore SQLite: {e}")
finally:
    if conn:
        conn.close()