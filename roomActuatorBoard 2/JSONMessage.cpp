#include "JSONMessage.h"

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
float Msg::getMeasure() { 
  return doc["measure"].as<float>();
}