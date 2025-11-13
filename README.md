# 🏡 Smart Home: Sistema Domotico IoT per il Controllo di una Stanza

## 🌟 1. Introduzione e Obiettivo del Progetto

Questo progetto implementa un sistema di **domotica intelligente (Smart Home)** basato su architettura **IoT (Internet of Things)**. L'obiettivo è fornire un controllo automatizzato e manuale degli attuatori (luci e tapparelle) all'interno di una stanza, basando le decisioni su sensori ambientali e orari.

Il sistema è suddiviso in moduli distinti che comunicano tramite il protocollo **MQTT** e un bridge **WebSocket** per l'interfaccia utente.

---

## 👥 2. Partecipanti al Progetto

| Ruolo | Nome Progettista | Email Progettista |
| :--- | :--- | :--- |
| Collaboratore 1 | Andruccioli Diego | diego.andruccioli@studio.unibo.it |
| Collaboratore 2 | Mici Rei | rei.mici2@studio.unibo.it |
| Collaboratore 3 | Morelli Giovanni | giovanni.morelli8@studio.unibo.it |

---

## ⚙️ 3. Componenti e Architettura

Il sistema è basato su un'architettura a tre livelli:

### A. Componenti Hardware (Microcontrollori)

| Modulo | Microcontrollore | Sensori/Attuatori |
| :--- | :--- | :--- |
| **Room Sensor Board** | ESP32 | Sensore PIR (movimento), Fotoresistenza (luminosità). |
| **Room Control (Attuatori)** | ESP32 | LED (simula Luce), Servomotore (simula Tapparella). |

### B. Componenti Software e Protocolli

| Modulo | Tecnologia Principale | Protocollo/Libreria | Ruolo |
| :--- | :--- | :--- | :--- |
| **Microcontrollori** | C++/Arduino | **MQTT** | Comunicazione D2D (Device-to-Device). |
| **Server Bridge** | Python / Flask | **MQTT / WebSocket** | Ponte tra la rete locale (MQTT) e l'interfaccia web (WS). |
| **Dashboard** | HTML / JS / Bootstrap | **WebSocket** | Interfaccia utente in tempo reale. |
| **Data Visualization** | JavaScript | Plotly.js | Rendering di grafici storici. |

---

## 💡 4. Funzionalità del Progetto

Il sistema supporta due modalità operative principali per ogni attuatore:

### Controllo Tapparelle (RollerShutter)
* **Modalità Automatica:** La tapparella si apre completamente (100%) se viene rilevato **movimento** (**PIR ON**) **E** l'orario rientra nella fascia "Giorno" (es. 08:00 - 19:00, gestito tramite NTP).
* **Modalità Manuale:** L'utente prende il controllo completo tramite uno *slider* sulla dashboard, impostando la posizione (0% - 100%).

### Controllo Luce (Light)
* **Modalità Automatica:** La luce si accende se viene rilevato **movimento** (**PIR ON**) **E** è buio (logica da implementare/simulare con la Fotoresistenza).
* **Modalità Manuale:** L'utente può forzare lo stato della luce (ON/OFF) tramite uno *switch* sulla dashboard.

**Priorità:** I comandi manuali hanno sempre la priorità sulla logica automatica.

---

## 🚦 5. Stato di Implementazione e Priorità delle Funzionalità

Questa tabella riepiloga le funzionalità principali del sistema e lo stato attuale dell'implementazione.

| Nome Funzione | Tipo Modulo | Priorità | Stato di Implementazione |
| :--- | :--- | :--- | :--- |
| **Luce: Controllo Manuale (ON/OFF)** | Attuatore / Dashboard | MUST | 🟢 |
| **Luce: Logica Automatica (PIR)** | Attuatore | SHOULD | 🟠 |
| **Tapparella: Controllo Manuale (Slider)** | Attuatore / Dashboard | MUST | 🟢 |
| **Tapparella: Logica Auto (PIR + Orario)** | Attuatore | MUST | 🟢 |
| **Monitoraggio Movimento (PIR)** | Sensori / Dashboard | MUST | 🟢 |
| **Monitoraggio Luminosità (LDR)** | Sensori / Dashboard | MUST | 🟢 |
| **Persistenza Dati Storici (DB)** | Server Bridge | SHOULD | 🟢 |
| **Server Bridge (MQTT $\leftrightarrow$ WS)** | Server Bridge | MUST | 🟢 |

<aside>
<img src="/icons/row_gray.svg" alt="/icons/row_gray.svg" width="40px" />
Legenda:

* **🟢 Completamente Implementato:** Funzione con codice sorgente completo e testato.
* **🟠 Implementato Parzialmente:** Logica base presente, ma mancano integrazioni o test completi (es. persistenza dati DB non ancora attiva).
* **🔴 Mancante:** Funzione non ancora sviluppata.
</aside>

---

## 📦 6. Setup delle Dipendenze

Per avviare il progetto, i collaboratori devono installare le librerie sia per l'ambiente Python (Bridge) sia per i microcontrollori (Arduino/C++).

### A. Dipendenze Python (Server Bridge)

1.  Creare e attivare l'ambiente virtuale (`venv`) nella cartella radice (`Progetto_VEM/`).
2.  Installare le librerie usando il file `requirements.txt` presente in `progetto/serverBridge/`:
    ```bash
    pip install -r progetto/serverBridge/requirements.txt
    ```

### B. Dipendenze Arduino/C++ (Librerie Aggiuntive)

Le seguenti librerie devono essere installate tramite il **Gestore Librerie dell'IDE Arduino**.

#### **`roomControl/roomActuatorBoard.ino` e file collegati (Logica di Controllo)**

* `Servo` (Libreria standard inclusa nell'IDE)
* `TimeLib` (Per la gestione dell'orario e la logica Giorno/Notte)
* `ArduinoJson` (Per il parsing dei messaggi JSON MQTT, consigliata v6)
* `PubSubClient` (Per la gestione della connettività MQTT)

#### **`roomSensorBoard/sensor-board.ino` (Scheda Sensori)**

* `WiFi` (Libreria standard inclusa nell'IDE)
* `NTPClient` (Per sincronizzare l'orario di sistema con un server NTP)
* `WiFiUdp` (Libreria standard, usata da NTPClient)
* `Adafruit_MQTT` (Libreria client MQTT leggera)
* `ArduinoJson` (Per la creazione dei payload JSON in uscita)
