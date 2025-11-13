#include "JSONMessage.h"
#include <ArduinoJson.h> 
#include <Arduino.h>

// Implementazione del Costruttore
// Usa Msg:: per dire che stai implementando il metodo di Msg
Msg::Msg(String content) : content(content) {
  deserializeJson(doc, content);
}

// Implementazione di getContent
String Msg::getContent() {
  return content;
}

// Implementazione di getSensorName
String Msg::getSensorName() {
  return doc["name"].as<String>();
}

// Implementazione di getTimestamp
long Msg::getTimestamp() {
  return doc["timestamp"].as<long>();
}

// Implementazione di getMeasure
int Msg::getMeasure() {
  return doc["measure"].as<int>();
}