// File: src/main.cpp

#include <Arduino.h>
#include <WiFi.h>
#include <PubSubClient.h>

// Includi le tue classi di logica (dalla cartella 'include/')
#include "JSONMessage.h"
#include "Light.h"
#include "RollerShutter.h"

// --- Configurazione di Rete ---
const char* ssid = "Wokwi-GUEST"; // Corrisponde al tuo wokwi.toml
const char* password = "";        // Corrisponde al tuo wokwi.toml

// --- Configurazione Broker MQTT ---
// !!! CONTROLLA QUESTO IP !!! Deve essere l'IP del tuo Mac dove gira Mosquitto
const char* mqtt_server = "6a7c8e41ebb842f4811d5f9e75cdffc4.s1.eu.hivemq.cloud"; 
const int mqtt_port = 8883;

// --- Configurazione Topic MQTT (Iscrizione) ---
const char* TOPIC_CMD_LIGHT = "cmd/light";  
const char* TOPIC_CMD_ROLL = "cmd/roll";
const char* TOPIC_PIR_SENSOR = "esp/motion";
const char* TOPIC_LIGHT_SENSOR = "esp/light";

// --- Configurazione Pin Attuatori ---
const int PIN_SERVO_ROLL = 2; // Pin per il servo (tapparella)
const int PIN_LED_LIGHT = 13; // Pin per il LED (luce)

// --- Oggetti di Sistema ---
WiFiClient espClient;
PubSubClient client(espClient); 

// --- Variabili di Stato Locali (Sincronizzazione) ---
int pirStateLocal = 0;
int lightSensorStateLocal = 0; 
int manualLightState = 0; 
int manualRollState = 0; 

// Dichiarazioni di funzioni (prototipi)
void connectToWIFI();
void connectToMQTT();
void mqttCallback(char* topic, byte* payload, unsigned int length);
// Nota: i prototipi per Light/RollerShutter sono già nei file .h

// =========================================================================
//                                   SETUP
// =========================================================================
void setup() {
  Serial.begin(115200);
  connectToWIFI();
  
  setupRoll(PIN_SERVO_ROLL); 
  pinMode(PIN_LED_LIGHT, OUTPUT);
  
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

  // Esegui la logica della luce (da Light.cpp)
  updateSensorStates(manualLightState, pirStateLocal);
  updateLight();
  applyLightState();
  
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
  String message = "";
  for (unsigned int i = 0; i < length; i++) {
    message += (char)payload[i];
  }
  Serial.print("Messaggio ricevuto su [");
  Serial.print(topic);
  Serial.print("]: ");
  Serial.println(message);

  // Usa la classe Msg (da JSONMessage.cpp)
  Msg msg(message);
  String name = msg.getSensorName();
  long timestamp = msg.getTimestamp();
  int measure = msg.getMeasure();

  // --- 1. Logica Tapparella (da RollerShutter.cpp) ---
  if (strcmp(topic, TOPIC_CMD_ROLL) == 0 || strcmp(topic, TOPIC_PIR_SENSOR) == 0) {
    
    if (name == "manual_roll") {
        manualRollState = measure; 
    } else if (name == "roll") {
        loopRoll(name, timestamp, measure); 
        return; 
    }
    
    if (name == "pir_sensor") {
      pirStateLocal = measure;
    }
    
    // Se è in modalità automatica (manualRollState == 0), chiama la logica automatica
    if (manualRollState == 0) {
      loopRoll("pir_sensor", timestamp, pirStateLocal); 
    } else if (name == "manual_roll") {
      loopRoll(name, timestamp, manualRollState);
    }

  // --- 2. Logica Luce (da Light.cpp) ---
  } else if (strcmp(topic, TOPIC_CMD_LIGHT) == 0 || strcmp(topic, TOPIC_LIGHT_SENSOR) == 0) {
    
    if (name == "manual_light") {
        manualLightState = measure; 
    } else if (name == "light") {
        if (manualLightState == 1) { 
          updateSensorStates(1, measure); 
        }
        return;
    }
    
    if (name == "pir_sensor") {
      pirStateLocal = measure;
    } 
    
    // (La logica luce viene eseguita nel loop() principale)
  }
}