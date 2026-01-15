#include <ArduinoJson.h>
#include <Arduino.h>
#include <WiFi.h>
#include <NTPClient.h>
#include <WiFiUdp.h>
#include <Adafruit_MQTT.h>
#include "Adafruit_MQTT_Client.h"
#include <WiFiClientSecure.h>
#include "DHT.h" 

#define PIR_PIN 34
#define DHTPIN 27     // Pin sensore temperatura
#define DHTTYPE DHT22 // Tipo sensore
#define LED_PIN 32

DHT dht(DHTPIN, DHTTYPE);

// --- Configurazione WiFi (per Wokwi) ---
const char* ssid = "Wokwi-GUEST";
const char* password = "";

// --- Configurazione Broker MQTT (HiveMQ) ---
const char* mqtt_server = "52dddef9726d430db26ad9b27548f562.s1.eu.hivemq.cloud";
const int mqtt_port = 8883;

const char* mqtt_user = "publish";
const char* mqtt_password = "Publish1";

// --- MODIFICA QUI: Topic "Grezzi" del Sensore ---
// Usiamo "sensor/" invece di "esp/" così l'attuatore non li ascolta direttamente
const char* topic_temp = "sensor/temperature";
const char* topic_motion = "sensor/motion";

unsigned long lastNotifyTime = 0;
const unsigned long notifyInterval = 2000;

// --- Oggetti Client ---
WiFiClientSecure espClient; 
Adafruit_MQTT_Client mqttClient(&espClient, mqtt_server, mqtt_port);
Adafruit_MQTT_Publish publisher_temp(&mqttClient, topic_temp);
Adafruit_MQTT_Publish publisher_motion(&mqttClient, topic_motion);
WiFiUDP ntpUDP;

NTPClient timeClient(ntpUDP, "pool.ntp.org", 7200);

// --- JSON helper ---
String getJson(const char* name, float measure) { 
  timeClient.update();
  StaticJsonDocument<128> doc;
  doc["name"] = name;
  doc["measure"] = measure;
  doc["timestamp"] = timeClient.getEpochTime();
  String json;
  serializeJson(doc, json);
  return json;
}

// --- Classe Pir ---
class Pir {
  int pirPin;
  int ledPin;

public:
  Pir(int p, int l) : pirPin(p), ledPin(l) {
    pinMode(pirPin, INPUT);
    pinMode(ledPin, OUTPUT);
    delay(5000);
    // Calibrazione PIR
  }
  int getMotion() {
    int motion = digitalRead(pirPin) == HIGH ? 1 : 0;
    digitalWrite(ledPin, motion ? HIGH : LOW);
    return motion;
  }
  String toJson() {
    return getJson("pir_sensor", getMotion());
  }
};

Pir pir(PIR_PIN, LED_PIN);

// --- Funzione Connessione WiFi ---
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

// --- Funzione Connessione MQTT ---
void connectToMQTT() {
  Serial.println("Connessione a MQTT (HiveMQ)...");
  espClient.setInsecure();

  while (!mqttClient.connected()) {
    Serial.print("Tentativo di connessione con utente: ");
    Serial.println(mqtt_user);
    uint8_t errorCode = mqttClient.connect(mqtt_user, mqtt_password);

    if (errorCode == 0) {
      Serial.println("MQTT connesso!");
    } else {
      Serial.print("Fallito. Codice errore: ");
      Serial.println(mqttClient.connectErrorString(errorCode)); 
      Serial.println("Ritento tra 5 secondi...");
      delay(5000);
    }
  }
}

void setup() {
  Serial.begin(115200);
  Serial.println("AVVIO SENSORE...");
  
  dht.begin(); // Avvio DHT
  
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
    
    // Lettura Temperatura
    float t = dht.readTemperature();
    if (!isnan(t)) {
        String json = getJson("temperature", t);
        if (publisher_temp.publish(json.c_str())) {
          Serial.print("Temp pubblicata: "); Serial.println(t);
        } else {
          Serial.println("Errore pubblicazione temp");
        }
    } else {
        Serial.println("Errore lettura DHT!");
    }

    // Invio Movimento
    if (publisher_motion.publish(pir.toJson().c_str())) {
      Serial.println("Valore movimento pubblicato");
    } else {
      Serial.println("Errore pubblicazione movimento");
    }
    lastNotifyTime = now;
  }
}