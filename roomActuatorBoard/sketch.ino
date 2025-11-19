#include <Arduino.h>
#include <WiFi.h>
#include <PubSubClient.h>
#include <WiFiClientSecure.h> 
#include <ArduinoJson.h>

#include "JSONMessage.h"
#include "Light.h"
#include "RollerShutter.h"

// --- CONFIGURAZIONE RETE ---
const char* ssid = "Wokwi-GUEST";
const char* password = "";

// --- CONFIGURAZIONE HIVEMQ ---
const char* mqtt_server = "52dddef9726d430db26ad9b27548f562.s1.eu.hivemq.cloud";
const int mqtt_port = 8883;
// Usa l'utente SUBSCRIBE
const char* MQTT_USER = "subscribe";
const char* MQTT_PASS = "Subscribe1"; 

const char* TOPIC_CMD_LIGHT = "cmd/light";
const char* TOPIC_CMD_ROLL = "cmd/roll";
const char* TOPIC_PIR_SENSOR = "esp/motion";
const char* TOPIC_LIGHT_SENSOR = "esp/light";

const int PIN_SERVO_ROLL = 2;
const int PIN_LED_LIGHT = 13;

WiFiClientSecure espClient;
PubSubClient client(espClient);

int pirStateLocal = 0;
int lightSensorStateLocal = 0;
int manualLightState = 0;
int manualRollState = 0;

void connectToWIFI() {
  Serial.print("Connetto a WiFi: ");
  Serial.println(ssid);
  WiFi.mode(WIFI_STA);
  WiFi.begin(ssid, password);
  while (WiFi.status() != WL_CONNECTED) {
    delay(500);
    Serial.print(".");
  }
  Serial.println("\nWiFi connesso.");
}

void connectToMQTT() {
  while (!client.connected()) {
    Serial.println("Connessione a HiveMQ...");
    espClient.setInsecure(); 

    String clientId = "ESP32_Act_" + String(random(0xffff), HEX);
    if (client.connect(clientId.c_str(), MQTT_USER, MQTT_PASS)) {
      Serial.println("MQTT connesso!");
      client.subscribe(TOPIC_CMD_LIGHT);
      client.subscribe(TOPIC_CMD_ROLL);
      client.subscribe(TOPIC_PIR_SENSOR);
      client.subscribe(TOPIC_LIGHT_SENSOR);
      Serial.println("Sottoscrizioni attive.");
    } else {
      Serial.print("Fallito, rc=");
      Serial.print(client.state());
      Serial.println(" riprovo tra 5s");
      delay(5000);
    }
  }
}

void mqttCallback(char* topic, byte* payload, unsigned int length) {
  String message = "";
  for (unsigned int i = 0; i < length; i++) {
    message += (char)payload[i];
  }
  Serial.print("Messaggio su [");
  Serial.print(topic);
  Serial.println("]");

  Msg msg(message);
  String name = msg.getSensorName();
  long timestamp = msg.getTimestamp();
  int measure = msg.getMeasure();

  if (strcmp(topic, TOPIC_CMD_ROLL) == 0 || strcmp(topic, TOPIC_PIR_SENSOR) == 0) {
    if (name == "manual_roll") manualRollState = measure;
    else if (name == "roll") { loopRoll(name, timestamp, measure); return; }
    
    if (name == "pir_sensor") pirStateLocal = measure;
    
    if (manualRollState == 0) loopRoll("pir_sensor", timestamp, pirStateLocal);
    else if (name == "manual_roll") loopRoll(name, timestamp, manualRollState);

  } else if (strcmp(topic, TOPIC_CMD_LIGHT) == 0 || strcmp(topic, TOPIC_LIGHT_SENSOR) == 0) {
    if (name == "manual_light") manualLightState = measure;
    else if (name == "light") {
        if (manualLightState == 1) updateSensorStates(1, measure);
        return;
    }
    if (name == "pir_sensor") pirStateLocal = measure;
  }
}

void setup() {
  Serial.begin(115200);
  connectToWIFI();
  setupRoll(PIN_SERVO_ROLL);
  pinMode(PIN_LED_LIGHT, OUTPUT);
  client.setServer(mqtt_server, mqtt_port);
  client.setCallback(mqttCallback);
  connectToMQTT();
}

void loop() {
  if (!client.connected()) connectToMQTT();
  client.loop();
  updateSensorStates(manualLightState, pirStateLocal);
  updateLight();
  applyLightState();
  delay(100);
}