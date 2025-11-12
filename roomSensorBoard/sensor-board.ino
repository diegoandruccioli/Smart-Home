#include <ArduinoJson.h>
#include <Arduino.h>
#include <WiFi.h>
#include <NTPClient.h>
#include <WiFiUdp.h>
#include <Adafruit_MQTT.h>
#include "Adafruit_MQTT_Client.h"

#define PIR_PIN 34
#define PHOTO_RESISTOR_PIN 35
#define LED_PIN 32

// --- Configurazione di Rete ---
const char* ssid = "Wokwi-GUEST";
const char* password = "";
const char* mqtt_server = "6a7c8e41ebb842f4811d5f9e75cdffc4.s1.eu.hivemq.cloud";
const int mqtt_port = 8883;
const char* topic_light = "esp/light";
const char* topic_motion = "esp/motion";

unsigned long lastNotifyTime = 0;
const unsigned long notifyInterval = 1000;

// MQTT client objects
WiFiClient espClient;
Adafruit_MQTT_Client mqttClient(&espClient, mqtt_server, mqtt_port);
Adafruit_MQTT_Publish publisher_light(&mqttClient, topic_light);
Adafruit_MQTT_Publish publisher_motion(&mqttClient, topic_motion);

// NTP client for timestamp
WiFiUDP ntpUDP;
NTPClient timeClient(ntpUDP, "pool.ntp.org", 7200);

// JSON helper - builds JSON string with name, measure and timestamp
String getJson(const char* name, int measure) {
  timeClient.update();
  StaticJsonDocument<128> doc; 
  doc["measure"] = measure;
  doc["timestamp"] = timeClient.getEpochTime();
  String json;
  serializeJson(doc, json);
  return json;
}

// Photoresistor sensor class (simplified)
class PhotoResistor {
  int pin;
public:
  PhotoResistor(int p) : pin(p) {
    pinMode(pin, INPUT);
  }
  int isDark() {
    return analogRead(pin) <= 3000 ? 1 : 0;
  }
  String toJson() {
    return getJson("photo_resistor", isDark());
  }
};

// PIR sensor class (simplified)
class Pir {
  int pirPin;
  int ledPin;
public:
  Pir(int p, int l) : pirPin(p), ledPin(l) {
    pinMode(pirPin, INPUT);
    pinMode(ledPin, OUTPUT);
    delay(5000);
  }
  int getMotion() {
    int motion = digitalRead(pirPin) == HIGH ? 1 : 0;
    analogWrite(ledPin, motion * 255);
    return motion;
  }
  String toJson() {
    return getJson("pir_sensor", getMotion());
  }
};

// Instantiate sensors
PhotoResistor resistor(PHOTO_RESISTOR_PIN);
Pir pir(PIR_PIN, LED_PIN);

// WiFi connection function
void connectToWIFI() {
  Serial.print("Connetto a WiFi: ");
  Serial.println(ssid);
  WiFi.mode(WIFI_STA);
  WiFi.begin(ssid, password);
  while (WiFi.status() != WL_CONNECTED) {
    delay(500);
  }
  Serial.print("WiFi connesso. IP: ");
  Serial.println(WiFi.localIP());
}

// MQTT connection function
void connectToMQTT() {
  Serial.println("Connessione a MQTT...");
  while (!mqttClient.connected()) {
    if (!mqttClient.connect()) {
      delay(500);
    }
  }
  Serial.println("MQTT connesso");
}

void setup() {
  Serial.begin(115200);
  connectToWIFI();
  timeClient.begin();
  timeClient.update();
  connectToMQTT();
}

void loop() {
  if (WiFi.status() != WL_CONNECTED) {
    Serial.println("WiFi perso, riconnessione...");
    connectToWIFI();
  }
  if (!mqttClient.ping()) {
    Serial.println("MQTT perso, riconnessione...");
    connectToMQTT();
  }
  unsigned long now = millis();
  if (now - lastNotifyTime >= notifyInterval) {
    if (publisher_light.publish(resistor.toJson().c_str())) {
      Serial.println("Valore luce pubblicato");
    } else {
      Serial.println("Errore pubblicazione luce");
    }
    if (publisher_motion.publish(pir.toJson().c_str())) {
      Serial.println("Valore movimento pubblicato");
    } else {
      Serial.println("Errore pubblicazione movimento");
    }
    lastNotifyTime = now;
  }
}
