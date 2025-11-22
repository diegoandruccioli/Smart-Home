# 🏡 Smart Home: Sistema Domotico IoT per il Controllo di una Stanza

## 🌟 1. Introduzione e Obiettivo del Progetto

Questo progetto implementa un sistema di **domotica intelligente (Smart Home)** basato su architettura **IoT (Internet of Things)**. L'obiettivo è fornire un controllo automatizzato e manuale degli attuatori (luci e tapparelle) all'interno di una stanza, basando le decisioni su sensori ambientali e orari.

Il sistema è suddiviso in moduli distinti che comunicano tramite il protocollo **MQTT** e un bridge **WebSocket** per l'interfaccia utente, garantendo persistenza dei dati e visualizzazione grafica dello storico.

---

## 👥 2. Partecipanti al Progetto

| Ruolo | Nome Progettista | Email Progettista |
| :--- | :--- | :--- |
| Collaboratore 1 | Andruccioli Diego | diego.andruccioli@studio.unibo.it |
| Collaboratore 2 | Mici Rei | rei.mici2@studio.unibo.it |
| Collaboratore 3 | Morelli Giovanni | giovanni.morelli8@studio.unibo.it |

---

## ⚙️ 3. Componenti e Architettura

Il sistema è basato su un'architettura a tre livelli interconnessi:

### A. Componenti Hardware (Microcontrollori)

| Modulo | Microcontrollore | Sensori/Attuatori |
| :--- | :--- | :--- |
| **Room Sensor Board** | ESP32 | **Sensore PIR** (Rilevamento movimento), **Fotoresistenza** (Monitoraggio luminosità). Invia dati telemetrici via MQTT. |
| **Room Control (Attuatori)** | ESP32 | **LED** (simula Luce), **Servomotore** (simula Tapparella). Riceve comandi ed esegue logiche automatiche locali. |

### B. Componenti Software e Protocolli

| Modulo | Tecnologia Principale | Protocollo/Libreria | Ruolo |
| :--- | :--- | :--- | :--- |
| **Microcontrollori** | C++/Arduino | **MQTT** (PubSubClient, Adafruit_MQTT) | Comunicazione D2D (Device-to-Device) e verso il server. |
| **Server Bridge** | Python / Flask | **MQTT / WebSocket / SQLite** | Ponte tra la rete locale (MQTT) e il web. Gestisce la persistenza dati su DB. |
| **Dashboard** | HTML / JS / Bootstrap | **WebSocket** | Interfaccia utente in tempo reale per monitoraggio e controllo. |
| **Data Visualization** | JavaScript / Plotly | **REST API** | Rendering di grafici storici basati sui dati salvati nel DB. |

---

## 🔗 4. Simulazione Online

È possibile testare il funzionamento dei circuiti direttamente nel browser tramite Wokwi:

* **Sensor Board (Sensori):** [Link al Progetto Wokwi](https://wokwi.com/projects/447411725151306753)
* **Actuator Board (Attuatori):** [Link al Progetto Wokwi](https://wokwi.com/projects/447413070768226305)

---

## 💡 5. Funzionalità del Progetto

Il sistema supporta modalità operative automatiche e manuali, oltre al monitoraggio storico.

### Controllo Tapparelle (RollerShutter)
* **Modalità Automatica:** La tapparella si apre completamente (100%) se viene rilevato **movimento** (**PIR ON**) **E** l'orario rientra nella fascia "Giorno" (es. 08:00 - 19:00, gestito localmente tramite timestamp).
* **Modalità Manuale:** L'utente prende il controllo completo tramite uno *slider* sulla dashboard, impostando la posizione (0% - 100%).

### Controllo Luce (Light)
* **Modalità Automatica:** La luce si accende automaticamente se viene rilevato **movimento** (**PIR ON**).
* **Modalità Manuale:** L'utente può forzare lo stato della luce (ON/OFF) tramite uno *switch* sulla dashboard, che ha priorità sui sensori.

**Priorità:** I comandi manuali hanno sempre la priorità sulla logica automatica.

### Monitoraggio e Storico
* **Dashboard Live:** Visualizzazione in tempo reale dello stato dei sensori (Movimento/Quiete, Buio/Luminoso).
* **Grafici Storici:** Il sistema registra ogni evento su database **SQLite**. La dashboard interroga le API del server per mostrare grafici interattivi sull'utilizzo della luce e l'apertura delle tapparelle negli ultimi minuti/ore.

---

## 🚦 6. Stato di Implementazione

Tutte le funzionalità previste sono state implementate, testate e integrate nel branch di sviluppo.

| Nome Funzione | Tipo Modulo | Priorità | Stato di Implementazione |
| :--- | :--- | :--- | :--- |
| **Luce: Controllo Manuale (ON/OFF)** | Attuatore / Dashboard | MUST | 🟢 |
| **Luce: Logica Automatica (PIR)** | Attuatore | SHOULD | 🟢 |
| **Tapparella: Controllo Manuale (Slider)** | Attuatore / Dashboard | MUST | 🟢 |
| **Tapparella: Logica Auto (PIR + Orario)** | Attuatore | MUST | 🟢 |
| **Monitoraggio Movimento (PIR)** | Sensori / Dashboard | MUST | 🟢 |
| **Monitoraggio Luminosità (LDR)** | Sensori / Dashboard | MUST | 🟢 |
| **Persistenza Dati Storici (DB)** | Server Bridge | SHOULD | 🟢 |
| **Visualizzazione Grafici (Plotly)** | Dashboard / API | SHOULD | 🟢 |
| **Server Bridge (MQTT $\leftrightarrow$ WS)** | Server Bridge | MUST | 🟢 |

<aside>
<img src="https://upload.wikimedia.org/wikipedia/commons/thumb/3/3b/Green_check.svg/600px-Green_check.svg.png" alt="check" width="20px" />
Legenda:

* **🟢 Completamente Implementato:** Funzione con codice sorgente completo, integrato e funzionante (inclusi DB e Grafici).
* **🟠 Implementato Parzialmente:** Logica base presente, ma mancano integrazioni o test completi.
* **🔴 Mancante:** Funzione non ancora sviluppata.
</aside>

---

## 🚀 7. Come Avviare il Progetto

Per eseguire il sistema in locale (Server + Dashboard):

1.  **Installare le dipendenze Python:**
    ```bash
    pip install -r serverBridge/requirements.txt
    ```
2.  **Avviare lo script principale:**
    Posizionarsi nella cartella `serverBridge` ed eseguire:
    ```bash
    python app.py
    ```
    *Questo comando avvierà automaticamente sia il server web Flask (porta 8000) che il worker per la gestione MQTT/WebSocket (porta 8080).*

3.  **Accedere alla Dashboard:**
    Aprire il browser all'indirizzo: [http://localhost:8000](http://localhost:8000)

---

## 📦 8. Setup delle Dipendenze di Sviluppo

### A. Dipendenze Python (Server Bridge)

Il file `requirements.txt` include le librerie necessarie per il backend:
* `Flask`: Web server per la dashboard e le API.
* `websockets`: Gestione della comunicazione real-time.
* `paho-mqtt`: Client MQTT per comunicare con le schede ESP32.
* `mysql-connector-python`: Driver database (Nota: Il progetto utilizza **SQLite** di default, che è integrato in Python).

### B. Dipendenze Arduino/C++ (Librerie Aggiuntive)

Le seguenti librerie devono essere installate tramite il **Gestore Librerie dell'IDE Arduino** o incluse nel progetto Wokwi.

#### **`roomControl` (Attuatori)**

* `ESP32Servo` (Per il controllo del servomotore su ESP32)
* `ArduinoJson` (Per il parsing dei messaggi JSON MQTT)
* `PubSubClient` (Per la gestione della connettività MQTT)
* *(Nota: La gestione oraria è implementata internamente senza `TimeLib`)*

#### **`roomSensorBoard` (Sensori)**

* `WiFi`, `WiFiClientSecure` (Librerie standard incluse nell'IDE)
* `NTPClient` (Per sincronizzare l'orario di sistema con un server NTP)
* `WiFiUdp` (Libreria standard, usata da NTPClient)
* `Adafruit MQTT Library` (Libreria client MQTT)
* `ArduinoJson` (Per la creazione dei payload JSON in uscita)