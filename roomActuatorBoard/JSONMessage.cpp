#include "JSONMessage.h"
#include <ArduinoJson.h> 
#include <Arduino.h>

Msg::Msg(String content) : content(content) {
  deserializeJson(doc, content);
}
String Msg::getContent() {
  return content;
}
String Msg::getSensorName() {
  return doc["name"].as<String>();
}
long Msg::getTimestamp() {
  return doc["timestamp"].as<long>();
}
int Msg::getMeasure() {
  return doc["measure"].as<int>();
}