#ifndef LIGHT_H
#define LIGHT_H

#include <Arduino.h>

void setupLight(int pin);
void updateSensorStates(int newManual, int newPIR);
void updateLight();
void applyLightState();
void printLightState();

#endif