#include <Arduino.h>
#include <WiFi.h>
#include <PubSubClient.h>
#include <WiFiClientSecure.h>

// Inclusione dei moduli personalizzati
#include "JSONMessage.h"
#include "Light.h"

// ============================================================
//  CONFIGURAZIONE
// ============================================================

// WiFi
const char* ssid = "Wokwi-GUEST";
const char* password = "";

// MQTT Broker
const char* mqtt_server = "52dddef9726d430db26ad9b27548f562.s1.eu.hivemq.cloud";
const int mqtt_port = 8883;
const char* mqtt_user = "subscribe";
const char* mqtt_pass = "Subscribe1";

// Topic MQTT (Sottoscrizione generica a cmd/# gestisce tutto)
const char* TOPIC_CMD_LIGHT = "cmd/light";

// Pin Hardware
const int PIN_BUZZER = 2;       // Pin Buzzer
const int PIN_LED_LIGHT = 13;   // Pin LED Luce

// Oggetti Client
WiFiClientSecure espClient;
PubSubClient client(espClient);

// Variabili di stato
int globalPirState = 0;
float globalTemp = 0.0;
bool acOn = false;
bool manualOverride = false; // Per evitare che il sensore sovrascriva subito il manuale

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
  float measure = msg.getMeasure();

  // --- SMISTAMENTO LOGICA ---

  // 1. LUCE (Manuale e Auto)
  if (name == "manual_light" || name == "light") {
     updateSensorStates((int)measure, globalPirState);
  }

  // 2. MOVIMENTO (Aggiorna stato PIR)
  if (name == "pir_sensor") {
     globalPirState = (int)measure;
     updateSensorStates(0, globalPirState); // Aggiorna luce se in auto
  }

  // 3. LOGICA CONDIZIONATORE (Buzzer)
  
  // A) Comando MANUALE dalla Dashboard (manual_ac o ac)
  if (name == "manual_ac" || name == "ac") {
      manualOverride = true; // Attiva override manuale temporaneo
      if ((int)measure == 1) {
          Serial.println("CMD: AC MANUALE ON");
          tone(PIN_BUZZER, 100); 
          acOn = true;
      } else {
          Serial.println("CMD: AC MANUALE OFF");
          noTone(PIN_BUZZER);
          acOn = false;
      }
  }
  
  // B) Comando AUTOMATICO dal Sensore (temperature)
  else if (name == "temperature") {
     globalTemp = measure;
     // La logica automatica agisce solo se NON abbiamo appena forzato un manuale
     // (Opzionale: puoi rimuovere !manualOverride se vuoi che il sensore abbia sempre priorità)
     
     if (globalTemp > 24.0) {
        if (!acOn) {
            Serial.println("AUTO: CALDO! AC ON");
            tone(PIN_BUZZER, 100);
            acOn = true;
            manualOverride = false; // Reset override quando scatta l'automatico
        }
     } else {
        if (acOn && !manualOverride) { // Spegne solo se non è forzato manuale ON
            Serial.println("AUTO: TEMP OK. AC OFF");
            noTone(PIN_BUZZER);
            acOn = false;
        }
     }
  }

  // Esegui aggiornamenti immediati LED
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
  
  setupLight(PIN_LED_LIGHT);
  pinMode(PIN_BUZZER, OUTPUT);
  digitalWrite(PIN_BUZZER, LOW);

  connectToWIFI();
  espClient.setInsecure();
  client.setServer(mqtt_server, mqtt_port);
  client.setCallback(mqttCallback);
  
  connectToMQTT();
}

void loop() {
  if (!client.connected()) connectToMQTT();
  client.loop();
  
  updateLight();
  applyLightState();
  
  delay(50); 
}