#include <Arduino.h>
#include <WiFi.h>
#include <PubSubClient.h>
#include <WiFiClientSecure.h>

#include "JSONMessage.h"
#include "Light.h"

// config wifi
const char* ssid = "Wokwi-GUEST";
const char* password = "";

// config broker mqtt
const char* mqtt_server = "52dddef9726d430db26ad9b27548f562.s1.eu.hivemq.cloud";
const int mqtt_port = 8883;

const char* mqtt_user = "subscribe";
const char* mqtt_pass = "Subscribe1";

// la ricezione effettiva avviene in connectToMQTT() tramite la
// sottoscrizione generica a "cmd/#" (che include anche questo topic).
const char* TOPIC_CMD_LIGHT = "cmd/light";

// pin Hardware
const int PIN_BUZZER = 2;       
const int PIN_LED_LIGHT = 13;  

// oggetti Client
WiFiClientSecure espClient;
PubSubClient client(espClient);

// variabili di stato
int globalPirState = 0;
float globalTemp = 0.0;
bool acOn = false;
bool manualOverride = false; // per evitare che il sensore sovrascriva il manuale


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

  // parsing del messaggio JSON
  Msg msg(message);
  String name = msg.getSensorName();
  float measure = msg.getMeasure();


  // LUCE (manuale e auto)
  if (name == "manual_light" || name == "light") {
     updateSensorStates((int)measure, globalPirState);
  }

  //  MOVIMENTO (aggiorna stato PIR)
  if (name == "pir_sensor") {
     globalPirState = (int)measure;
     updateSensorStates(0, globalPirState); // aggiorna luce se in auto
  }

  // LOGICA CONDIZIONATORE (Buzzer)
  
  // !! comando MANUALE dalla dashboard (manual_ac o ac)
  if (name == "manual_ac" || name == "ac") {
      manualOverride = true; // attiva override manuale temporaneo
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
  
  // comando AUTOMATICO dal Sensore (temperature)
  else if (name == "temperature") {
     globalTemp = measure;
     // !! la logica automatica agisce solo se NON abiamo appena forzato un manuale
     
     if (globalTemp > 24.0) {
        if (!acOn) {
            Serial.println("AUTO: CALDO! AC ON");
            tone(PIN_BUZZER, 100);
            acOn = true;
            manualOverride = false; // reset override quando scatta l'automatico
        }
     } else {
        if (acOn && !manualOverride) { // spegne solo se non è forzato manuale ON
            Serial.println("AUTO: TEMP OK. AC OFF");
            noTone(PIN_BUZZER);
            acOn = false;
        }
     }
  }

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
