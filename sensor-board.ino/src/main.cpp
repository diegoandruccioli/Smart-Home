// file: roomSensorBoard/main.cpp

#include <Arduino.h>
#include <WiFi.h>
#include <NTPClient.h>
#include <WiFiUdp.h>
#include <Adafruit_MQTT.h>
#include "Adafruit_MQTT_Client.h"
#include <ArduinoJson.h> 
// Importante: Aggiungi WiFiClientSecure per la connessione SSL (porta 8883)
#include <WiFiClientSecure.h>

#define PIR_PIN 34
#define PHOTO_RESISTOR_PIN 35
#define LED_PIN 32

// --- Configurazione WiFi ---
// Queste credenziali devono corrispondere a quelle nel tuo file wokwi.toml
const char* ssid = "Wokwi-GUEST";
const char* password = "";

// --- Configurazione Broker MQTT (HiveMQ) ---
const char* mqtt_server = "6a7c8e41ebb842f4811d5f9e75cdffc4.s1.eu.hivemq.cloud";
const int mqtt_port = 8883; // Porta 8883 per SSL/TLS
const char* mqtt_user = "bothrei"; // <-- METTI QUI IL TUO USERNAME HIVEMQ
const char* mqtt_password = "Bothrei1"; // <-- METTI QUI LA TUA PASSWORD HIVEMQ

// --- Topic MQTT ---
const char* topic_light = "esp/light";
const char* topic_motion = "esp/motion";

unsigned long lastNotifyTime = 0;
const unsigned long notifyInterval = 1000;

// --- Oggetti Client ---
// 1. Usa WiFiClientSecure per la connessione SSL alla porta 8883
WiFiClientSecure espClient;

// 2. Passa il client sicuro a Adafruit MQTT
Adafruit_MQTT_Client mqttClient(&espClient, mqtt_server, mqtt_port);

// Oggetti Publisher (invariati)
Adafruit_MQTT_Publish publisher_light(&mqttClient, topic_light);
Adafruit_MQTT_Publish publisher_motion(&mqttClient, topic_motion);

// Client NTP (invariato)
WiFiUDP ntpUDP;
NTPClient timeClient(ntpUDP, "pool.ntp.org", 7200);

// Funzione getJson (invariata, ma assicurati che 'name' sia incluso)
String getJson(const char* name, int measure) {
  timeClient.update();
  StaticJsonDocument<128> doc; 
  doc["name"] = name;
  doc["measure"] = measure;
  doc["timestamp"] = timeClient.getEpochTime();
  String json;
  serializeJson(doc, json);
  return json;
}

// Classe PhotoResistor (invariata)
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

// Classe Pir (invariata)
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

// Istanze sensori (invariate)
PhotoResistor resistor(PHOTO_RESISTOR_PIN);
Pir pir(PIR_PIN, LED_PIN);

// Funzione Connessione WiFi (invariata)
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

// --- Funzione Connessione MQTT (MODIFICATA) ---
void connectToMQTT() {
  Serial.println("Connessione a MQTT (HiveMQ)...");

  // Per ESP32, è buona norma impostare il client SSL per
  // non validare il certificato CA (più semplice per Wokwi/test)
  espClient.setInsecure(); // Salta la validazione del certificato

  while (!mqttClient.connected()) {
    Serial.print("Tentativo di connessione con utente: ");
    Serial.println(mqtt_user);

    // 3. Passa utente e password al .connect()
    if (mqttClient.connect(mqtt_user, mqtt_password)) {
      Serial.println("MQTT connesso!");
    } else {
      Serial.print("Fallito. Codice errore: ");
      // Stampa l'errore specifico per il debug
      //Serial.println(mqttClient.connectErrorString(mqttClient.connectError()));
      Serial.println("Ritento tra 5 secondi...");
      delay(5000);
    }
  }
}

void setup() {
  Serial.begin(115200);
  connectToWIFI();
  timeClient.begin();
  timeClient.update();
  
  // Aggiunto per il debug SSL su ESP32 (opzionale)
  // espClient.setDebug(true); 

  connectToMQTT();
}

// Funzione Loop (invariata)
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