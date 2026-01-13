#include <Arduino.h>
#include <WiFi.h>
#include <PubSubClient.h>
#include <WiFiClientSecure.h>

// Inclusione dei moduli personalizzati
#include "JSONMessage.h"
#include "Light.h"
#include "RollerShutter.h"

// ============================================================
//  CONFIGURAZIONE
// ============================================================

// WiFi (Wokwi Guest è standard per il simulatore)
const char* ssid = "Wokwi-GUEST";
const char* password = "";

// MQTT Broker (HiveMQ Cloud)
const char* mqtt_server = "52dddef9726d430db26ad9b27548f562.s1.eu.hivemq.cloud";
const int mqtt_port = 8883;
const char* mqtt_user = "subscribe"; // Utente creato per l'attuatore
const char* mqtt_pass = "Subscribe1";

// Topic MQTT
const char* TOPIC_CMD_LIGHT = "cmd/light";      // Comandi manuali per la luce
const char* TOPIC_CMD_ROLL = "cmd/roll";        // Comandi manuali per la tapparella
const char* TOPIC_PIR_SENSOR = "esp/motion";    // Dati dal sensore di movimento
const char* TOPIC_LIGHT_SENSOR = "esp/light";   // Dati dal sensore di luce

// Pin Hardware
const int PIN_SERVO_ROLL = 2;   // Pin Servo Motore
const int PIN_LED_LIGHT = 13;   // Pin LED Luce

// Oggetti Client
WiFiClientSecure espClient;
PubSubClient client(espClient);

// Variabile di supporto per stato PIR globale
int globalPirState = 0; 

// ============================================================
//  FUNZIONI DI RETE
// ============================================================

void connectToWIFI() {
  Serial.print("Connessione WiFi");
  WiFi.mode(WIFI_STA);
  WiFi.begin(ssid, password);
  while (WiFi.status() != WL_CONNECTED) {
    delay(500);
    Serial.print(".");
  }
  Serial.println("\nWiFi Connesso.");
}

void mqttCallback(char* topic, byte* payload, unsigned int length) {
  String message = "";
  for (unsigned int i = 0; i < length; i++) {
    message += (char)payload[i];
  }
  Serial.print("MSG: "); Serial.println(message);

  // Parsing del messaggio JSON
  Msg msg(message);
  String name = msg.getSensorName();
  int measure = msg.getMeasure();
  long timestamp = msg.getTimestamp();

  // --- SMISTAMENTO LOGICA ---

  // A) Logica Tapparella (Comandi manuali e sensori)
  if (name == "roll" || name == "manual_roll" || name == "pir_sensor") {
     loopRoll(name, timestamp, measure);
  }

  // B) Aggiornamento variabile PIR globale
  if (name == "pir_sensor") {
     globalPirState = measure;
     // Se la luce è in automatico, aggiorna in base al PIR
     updateSensorStates(0, globalPirState); 
  }

  // C) Logica Luce (Comandi Manuali)
  if (name == "manual_light") {
     // Attiva/Disattiva manuale luce
     updateSensorStates(measure, globalPirState);
  }
  else if (name == "light") {
     // Comando ON/OFF dalla dashboard
     updateSensorStates(measure, globalPirState);
  }

  // Esegui aggiornamenti immediati
  updateRollState();
  updateLight();
  applyLightState();
}

void connectToMQTT() {
  while (!client.connected()) {
    Serial.println("Connessione MQTT...");
    String clientId = "ESP32_Act_" + String(random(0xffff), HEX);
    
    if (client.connect(clientId.c_str(), mqtt_user, mqtt_pass)) {
      Serial.println("Connesso!");
      client.subscribe("esp/#"); 
      client.subscribe("cmd/#"); 
    } else {
      Serial.print("Err: "); Serial.print(client.state());
      delay(2000);
    }
  }
}

// ============================================================
//  SETUP & LOOP
// ============================================================

void setup() {
  Serial.begin(115200);
  
  // Setup Hardware
  setupRoll(PIN_SERVO_ROLL);
  setupLight(PIN_LED_LIGHT); // Configura il pin LED

  // Connessioni
  connectToWIFI();
  espClient.setInsecure(); // Necessario per Wokwi
  client.setServer(mqtt_server, mqtt_port);
  client.setCallback(mqttCallback);
  
  connectToMQTT();
}

void loop() {
  if (!client.connected()) connectToMQTT();
  client.loop();
  
  // Aggiornamento continuo attuatori
  updateRollState();
  updateLight();
  applyLightState();
  
  delay(50); 
}