# FILE: serverBridge/test_populate.py

import sqlite3
import time
import os
import random
from datetime import datetime

# Importa il percorso corretto da variable.py
from variable import DB_NAME 

# Blocco di Sicurezza
if not os.path.exists(DB_NAME):
    print(f"Errore: Database '{DB_NAME}' non trovato.")
    print("Avvia prima 'app.py' (Ctrl+C) per crearlo, poi esegui questo script.")
    exit()

# --- Definizione dei Dati di Test (Densi) ---
now = int(time.time())
minute = 60
processed_data = [] # Lista finale per l'inserimento

print("Generazione dati di test al minuto per le ultime 3 ore...")

# Simula dati per le ultime 3 ore (180 minuti)
for i in range(180):
    # Timestamp per ogni minuto passato
    ts = now - (i * minute)
    # Calcola la stringa leggibile
    dt_string = datetime.fromtimestamp(ts).strftime('%Y-%m-%d %H:%M:%S')
    
    # Simula Dati LUCE (0 o 1)
    if i > 60: # Nelle prime 2 ore
        light_measure = 1 if random.random() > 0.5 else 0
    else: # Nell'ultima ora
        light_measure = 1 if random.random() > 0.1 else 0
    
    processed_data.append((ts, dt_string, "light", light_measure))
        
    # Simula Dati TAPPARELLA (0-100)
    roll_position = max(0, min(100, (i / 1.8) * (random.uniform(0.9, 1.1))))
    processed_data.append((ts, dt_string, "roll", int(roll_position)))


# --- Blocco Esecuzione Database ---
try:
    conn = sqlite3.connect(DB_NAME)
    cursor = conn.cursor()
    
    print(f"Connesso a {DB_NAME}. Inserimento di {len(processed_data)} record di test...")
    
    # Query di inserimento per la tabella a 4 colonne
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