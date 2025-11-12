#include <Arduino.h>
#include <WiFi.h>
#include <PubSubClient.h>

// Includi le tue classi di logica
#include "JSONMessage.h"
#include "Light.h"
#include "RollerShutter.h"

// --- Configurazione di Rete ---
const char* ssid = "asus";                  // Dalla tua sensor-board.ino
const char* password = "0123456789";        // Dalla tua sensor-board.ino
const char* mqtt_server = "172.20.10.8";    // Broker MQTT
const int mqtt_port = 1883;

// --- Configurazione Topic MQTT (Iscrizione) ---
// Comandi manuali dalla dashboard (tramite il bridge Python)
const char* TOPIC_CMD_LIGHT = "cmd/light";  
const char* TOPIC_CMD_ROLL = "cmd/roll";
// Dati sensori dalla Scheda Sensori (per logica automatica)
const char* TOPIC_PIR_SENSOR = "esp/motion";
const char* TOPIC_LIGHT_SENSOR = "esp/light";

// --- Configurazione Pin Attuatori ---
const int PIN_SERVO_ROLL = 2; // Esempio di pin per il servo (tapparella)
const int PIN_LED_LIGHT = 13; // Già definito in Light.cpp, ma manteniamo per coerenza

// --- Oggetti di Sistema ---
WiFiClient espClient;
PubSubClient client(espClient); // Usiamo PubSubClient per il modulo Attuatori
// La tua logica
void setupRoll(int pin); // Prototipo (da RollerShutter.cpp)
void loopRoll(String sensorName, long timestamp, int measure); // Prototipo (da RollerShutter.cpp)

// --- Variabili di Stato Locali (Sincronizzazione) ---
int pirStateLocal = 0;
int lightSensorStateLocal = 0; 
int manualLightState = 0; 
int manualRollState = 0; 

// Dichiarazioni di funzioni
void connectToWIFI();
void connectToMQTT();
void mqttCallback(char* topic, byte* payload, unsigned int length);


// =========================================================================
//                                   SETUP
// =========================================================================
void setup() {
  Serial.begin(115200);
  connectToWIFI();
  
  // 1. Inizializza il servo tapparella
  setupRoll(PIN_SERVO_ROLL); 
  
  // 2. Setup del pin LED (già fatto in setup() di Light.cpp, ma replicato qui se usato come modulo)
  pinMode(PIN_LED_LIGHT, OUTPUT);
  
  // 3. Configura il client MQTT
  client.setServer(mqtt_server, mqtt_port);
  client.setCallback(mqttCallback);

  connectToMQTT();
}

// =========================================================================
//                                   LOOP
// =========================================================================
void loop() {
  if (!client.connected()) {
    connectToMQTT();
  }
  client.loop(); 

  // --- 1. Logica Luce (Esecuzione) ---
  // Aggiorna lo stato della luce in base allo stato sincronizzato
  // Nota: Light.cpp usa un loop bloccante, quindi dobbiamo chiamare solo le funzioni di aggiornamento
  updateSensorStates(manualLightState, pirStateLocal);
  updateLight();
  applyLightState();
  // printLightState(); // Per debug
  
  // --- 2. Logica Tapparella (Esecuzione) ---
  // Eseguita all'interno della callback Roll, per maggiore reattività, ma possiamo anche chiamarla qui
  // loopRoll("pir_sensor", now(), pirStateLocal); // Esempio se volessimo usare solo stati locali
  
  delay(100); 
}

// =========================================================================
//                             FUNZIONI DI RETE
// =========================================================================

void connectToWIFI() {
  Serial.print("Connetto a WiFi: ");
  Serial.println(ssid);
  WiFi.mode(WIFI_STA);
  WiFi.begin(ssid, password);
  while (WiFi.status() != WL_CONNECTED) {
    delay(500);
    Serial.print(".");
  }
  Serial.print("\nWiFi connesso. IP: ");
  Serial.println(WiFi.localIP());
}

void connectToMQTT() {
  while (!client.connected()) {
    Serial.println("Tentativo di connessione MQTT...");
    // Creazione ID Client casuale
    String clientId = "ESP32_Actuator_";
    clientId += String(random(0xffff), HEX);
    
    if (client.connect(clientId.c_str())) {
      Serial.println("MQTT connesso");
      
      // Iscrizione a tutti i topic
      client.subscribe(TOPIC_CMD_LIGHT);
      client.subscribe(TOPIC_CMD_ROLL);
      client.subscribe(TOPIC_PIR_SENSOR);
      client.subscribe(TOPIC_LIGHT_SENSOR);
      
      Serial.println("Sottoscrizioni effettuate.");
      
    } else {
      Serial.print("fallito, rc=");
      Serial.print(client.state());
      Serial.println(" ritento tra 5 secondi");
      delay(5000);
    }
  }
}

// =========================================================================
//                            CALLBACK MQTT
// =========================================================================

void mqttCallback(char* topic, byte* payload, unsigned int length) {
  // Converte il payload in stringa
  String message = "";
  for (unsigned int i = 0; i < length; i++) {
    message += (char)payload[i];
  }
  Serial.print("Messaggio ricevuto su [");
  Serial.print(topic);
  Serial.print("]: ");
  Serial.println(message);

  // Usa la tua classe per deserializzare il messaggio JSON
  Msg msg(message);
  String name = msg.getSensorName();
  long timestamp = msg.getTimestamp();
  int measure = msg.getMeasure();

  // --- 1. Aggiornamento Logica Tapparella (RollerShutter.cpp) ---
  if (strcmp(topic, TOPIC_CMD_ROLL) == 0 || strcmp(topic, TOPIC_PIR_SENSOR) == 0) {
    
    if (name == "manual_roll") {
        manualRollState = measure; // 1 (ON) o 0 (OFF)
        // La logica automatica in RollerShutter si attiva/disattiva qui
    } else if (name == "roll") {
        // Comando diretto da slider (forza lo stato)
        loopRoll(name, timestamp, measure); 
        return; 
    }
    
    // Aggiornamento dello stato del sensore PIR o Light Sensor
    if (name == "pir_sensor") {
      pirStateLocal = measure;
    }
    
    // Se è in modalità automatica (manualRollState == 0), chiama la logica automatica
    if (manualRollState == 0) {
      loopRoll("pir_sensor", timestamp, pirStateLocal); 
    } else if (name == "manual_roll") {
      // Se è passato in manuale (manual_roll=1), deve mantenere lo stato corrente
      // In RollerShutter.cpp: se manualState=1, l'updateRollState si ferma.
      loopRoll(name, timestamp, manualRollState);
    }

  // --- 2. Aggiornamento Logica Luce (Light.cpp) ---
  } else if (strcmp(topic, TOPIC_CMD_LIGHT) == 0 || strcmp(topic, TOPIC_LIGHT_SENSOR) == 0) {
    
    if (name == "manual_light") {
        manualLightState = measure; // 1 (Manuale) o 0 (Automatico)
    } else if (name == "light") {
        // Comando diretto da switch (forza lo stato)
        if (manualLightState == 1) { // Applica solo se in modalità manuale
          updateSensorStates(1, measure); // Forza manualState a 1, e misura a measure
        }
        return;
    }
    
    // Aggiornamento dello stato del sensore PIR/Light (solo se in modalità automatica)
    if (name == "pir_sensor") {
      pirStateLocal = measure;
    } 
    
    // La logica di updateLight viene eseguita nel loop() in base a manualLightState e pirStateLocal
  }
}

// Fine del file roomActuatorBoard.ino