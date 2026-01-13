#ifndef ROLLERSHUTTER_H
#define ROLLERSHUTTER_H

#include <Arduino.h>

void setupRoll(int pin);
void loopRoll(String sensorName, long timestamp, int measure);
void updateRollState();
void handleMessage(String sensorName, long timestamp, int measure);

#endif