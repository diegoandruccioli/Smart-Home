#include "JSONMessage.h"
#include <ArduinoJson.h> 
#include <Arduino.h>

// Classe semplice per messaggi JSON
class Msg {
private:
  String content;
  StaticJsonDocument<128> doc;

public:
  // Costruttore: riceve stringa JSON e deserializza
  Msg(String content) : content(content) {
    deserializeJson(doc, content);
  }

  // Restituisce contenuto JSON originale
  String getContent() {
    return content;
  }

  // Estrae il campo "name" dal JSON
  String getSensorName() {
    return doc["name"].as<String>();
  }

  // Estrae il campo "timestamp" dal JSON
  long getTimestamp() {
    return doc["timestamp"].as<long>();
  }

  // Estrae il campo "measure" dal JSON
  int getMeasure() {
    return doc["measure"].as<int>();
  }
};