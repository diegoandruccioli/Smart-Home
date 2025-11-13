# FILE: serverBridge/test_populate.py
import sqlite3
import time
import os

# Assicurati che il nome del DB corrisponda a quello in variable.py
DB_NAME = "smart_home.db"

# Controllo se il DB esiste
if not os.path.exists(DB_NAME):
    print(f"Errore: Database '{DB_NAME}' non trovato.")
    print("Avvia prima 'app.py' per crearlo.")
    exit()

# Dati di test: (timestamp, name, measure)
# Creiamo timestamp fittizi per le ultime ore
now = int(time.time())
hour = 3600

test_data = [
    # Dati LUCE (0 o 1)
    (now - 3*hour, "light", 1), # 3 ore fa (media 50%)
    (now - 3*hour + 600, "light", 0), 
    
    (now - 2*hour, "light", 1), # 2 ore fa (media 100%)
    (now - 2*hour + 600, "light", 1),
    
    (now - 1*hour, "light", 0), # 1 ora fa (media 0%)
    
    # Dati TAPPARELLA (0-100)
    (now - 3*hour, "roll", 100), # 3 ore fa (media 75%)
    (now - 3*hour + 600, "roll", 50),
    
    (now - 2*hour, "roll", 20), # 2 ore fa (media 25%)
    (now - 2*hour + 600, "roll", 30),
    
    (now - 1*hour, "roll", 80), # 1 ora fa (media 80%)
]

try:
    conn = sqlite3.connect(DB_NAME)
    cursor = conn.cursor()
    
    print(f"Connesso a {DB_NAME}. Inserimento di {len(test_data)} record di test...")
    
    cursor.executemany(
        "INSERT INTO sensor_data (timestamp, name, measure) VALUES (?, ?, ?)",
        test_data
    )
    
    conn.commit()
    print(f"Dati inseriti con successo. {conn.total_changes} righe modificate.")
    
except sqlite3.Error as e:
    print(f"Errore SQLite: {e}")
finally:
    if conn:
        conn.close()