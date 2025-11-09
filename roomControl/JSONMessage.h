#ifndef JSONMESSAGE_H
#define JSONMESSAGE_H

#include <Arduino.h>
#include <ArduinoJson.h>

// Definizione della classe Msg
class Msg {
private:
  String content;
  StaticJsonDocument<128> doc; // Come nel tuo .cpp

public:
  Msg(String content); // Costruttore
  String getContent();
  String getSensorName();
  long getTimestamp();
  int getMeasure();
};

#endif