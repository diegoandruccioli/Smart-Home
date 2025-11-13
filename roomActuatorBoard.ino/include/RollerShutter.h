#ifndef ROLLERSHUTTER_H
#define ROLLERSHUTTER_H

#include <Arduino.h>

// Prototipi delle funzioni
void setupRoll(int pin);
void loopRoll(String sensorName, long timestamp, int measure);

// Funzioni interne (opzionale dichiararle qui, ma è pulito)
void setTimeFromTimestamp(long timestamp);
void updateRollState();
void handleMessage(String sensorName, long timestamp, int measure);

#endif