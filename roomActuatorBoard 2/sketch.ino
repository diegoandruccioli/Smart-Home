#include <Arduino.h>
#include <WiFi.h>
#include <PubSubClient.h>
#include <WiFiClientSecure.h>

// Inclusione dei moduli personalizzati
#include "JSONMessage.h"
#include "Light.h"
// RIMOSSO RollerShutter.h

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

// Topic MQTT
const char* TOPIC_CMD_LIGHT = "cmd/light";
const char* TOPIC_PIR_SENSOR = "esp/motion";
const char* TOPIC_TEMP_SENSOR = "esp/temperature"; 

// Pin Hardware
const int PIN_BUZZER = 2;       // Pin Buzzer (Al posto del servo)
const int PIN_LED_LIGHT = 13;   // Pin LED Luce (Invariato)

// Oggetti Client
WiFiClientSecure espClient;
PubSubClient client(espClient);

// Variabile di supporto
int globalPirState = 0;
float globalTemp = 0.0;
bool acOn = false;

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
  long timestamp = msg.getTimestamp();

  // --- SMISTAMENTO LOGICA ---

  // A) Logica Luce (Comandi Manuali)
  if (name == "manual_light") {
     updateSensorStates((int)measure, globalPirState);
  }
  else if (name == "light") {
     updateSensorStates((int)measure, globalPirState);
  }

  // B) Aggiornamento variabile PIR globale
  if (name == "pir_sensor") {
     globalPirState = (int)measure;
     // Aggiorna luce in base al movimento (se in auto)
     updateSensorStates(0, globalPirState);
  }

  // C) Logica "Condizionatore" (Buzzer)
  if (name == "temperature") {
     globalTemp = measure;
     Serial.print("Temp: "); Serial.println(globalTemp);
     
     // SOGLIA: se > 24 gradi, accendi "AC" (Buzzer)
     if (globalTemp > 24.0) {
        if (!acOn) {
            Serial.println("CALDO! AC ACCESO");
            tone(PIN_BUZZER, 100); // Ronzio basso
            acOn = true;
        }
     } else {
        if (acOn) {
            Serial.println("TEMP OK. AC SPENTO");
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
  
  // Setup Hardware
  setupLight(PIN_LED_LIGHT);
  pinMode(PIN_BUZZER, OUTPUT);
  digitalWrite(PIN_BUZZER, LOW);

  // Connessioni
  connectToWIFI();
  espClient.setInsecure();
  client.setServer(mqtt_server, mqtt_port);
  client.setCallback(mqttCallback);
  
  connectToMQTT();
}

void loop() {
  if (!client.connected()) connectToMQTT();
  client.loop();
  
  // Aggiornamento continuo LED
  updateLight();
  applyLightState();
  
  delay(50); 
}