#ifndef JSONMESSAGE_H
#define JSONMESSAGE_H

#include <Arduino.h>
#include <ArduinoJson.h>

class Msg {
private:
  String content;
  StaticJsonDocument<256> doc;
public:
  Msg(String content); 
  String getContent();
  String getSensorName();
  long getTimestamp();
  float getMeasure(); 
};

#endif