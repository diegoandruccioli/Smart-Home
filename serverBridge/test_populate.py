# ---
# OBIETTIVO:
# Script di utilità per popolare il database con dati di test.
# Questo NON è parte del server, va eseguito manualmente UNA SOLA VOLTA
# per avere dati storici da visualizzare nei grafici.
# ---

# Importa la libreria 'sqlite3' per interagire con il database
import sqlite3
# Importa 'time' per generare timestamp (secondi)
import time
# Importa 'os' per controllare se il file del database esiste
import os

# --- CORREZIONE FONDAMENTALE ---
# NON definire DB_NAME qui. Importalo da 'variable.py'
# in modo che questo script scriva ESATTAMENTE nello stesso database
# usato da 'app.py' e dal 'worker'.
from variable import DB_NAME 

# --- Blocco di Sicurezza ---

# Controlla se il file del database (definito in variable.py) esiste già
if not os.path.exists(DB_NAME):
    # Se non esiste, ferma lo script
    print(f"Errore: Database '{DB_NAME}' non trovato.")
    # (Il database viene creato all'avvio di 'app.py' tramite 'init_db()')
    print("Avvia prima 'app.py' per crearlo.")
    # Esce dallo script
    exit()

# --- Definizione dei Dati di Test ---

# Ottiene l'ora corrente in secondi dal 1970 (timestamp UNIX)
now = int(time.time())
# Definisce una costante per 1 ora (60 secondi * 60 minuti)
hour = 3600

# Crea una lista di tuple. Ogni tupla rappresenta una riga del database
# Il formato è (timestamp, name, measure)
# Questo formato DEVE corrispondere alla query 'INSERT' qui sotto
test_data = [
    # Dati LUCE (measure = 0 o 1)
    # (Timestamp fittizio, nome sensore, valore)
    (now - 3*hour, "light", 1), # 3 ore fa, luce ACCESA
    (now - 3*hour + 600, "light", 0), # 3 ore fa (ma 10 min dopo), luce SPENTA
    
    (now - 2*hour, "light", 1), # 2 ore fa, luce ACCESA
    (now - 2*hour + 600, "light", 1), # 2 ore fa (10 min dopo), luce ACCESA
    
    (now - 1*hour, "light", 0), # 1 ora fa, luce SPENTA
    
    # Dati TAPPARELLA (measure = 0-100)
    (now - 3*hour, "roll", 100), # 3 ore fa, tapparella APERTA (100%)
    (now - 3*hour + 600, "roll", 50), # 3 ore fa (10 min dopo), tapparella a METÀ (50%)
    
    (now - 2*hour, "roll", 20), # 2 ore fa, tapparella al 20%
    (now - 2*hour + 600, "roll", 30), # 2 ore fa (10 min dopo), tapparella al 30%
    
    (now - 1*hour, "roll", 80), # 1 ora fa, tapparella all'80%
]

# --- Blocco Esecuzione Database ---

# 'try...finally' assicura che la connessione al DB venga chiusa
# anche se si verifica un errore durante l'inserimento.
try:
    # Si connette al database (usando il percorso corretto importato)
    conn = sqlite3.connect(DB_NAME)
    # Crea un cursore per eseguire comandi
    cursor = conn.cursor()
    
    # Stampa un feedback nel terminale
    print(f"Connesso a {DB_NAME}. Inserimento di {len(test_data)} record di test...")
    
    # Esegue l'inserimento di MOLTE righe (TUTTA la lista 'test_data')
    # 'executemany' è molto più veloce di un loop 'for'
    cursor.executemany(
        # La query SQL: inserisce 3 valori nelle 3 colonne specificate
        # I '?' sono segnaposto (placeholder)
        "INSERT INTO sensor_data (timestamp, name, measure) VALUES (?, ?, ?)",
        # La lista di dati (ogni tupla nella lista sostituirà i '?' per una riga)
        test_data
    )
    
    # 'commit()' salva permanentemente le modifiche nel file del database
    conn.commit()
    # Stampa un messaggio di successo
    print(f"Dati inseriti con successo. {conn.total_changes} righe modificate.")
    
except sqlite3.Error as e:
    # Se la query fallisce (es. tabella non esiste, permessi mancanti)
    print(f"Errore SQLite: {e}")
finally:
    # Blocco 'finally': viene eseguito SEMPRE (sia dopo 'try' che dopo 'except')
    if conn:
        # Se la connessione ('conn') esiste ancora, chiudila
        conn.close()