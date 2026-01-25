#include "Light.h" 
#include <Arduino.h>

int _lightPin; 

int light_pirState = 0;
int light_lightState = 0;
int light_manualState = 0;

void setupLight(int pin) {
  _lightPin = pin;
  pinMode(_lightPin, OUTPUT); // configura il pin come output
}

void updateSensorStates(int newManual, int newPIR) {
  light_manualState = newManual;
  light_pirState = newPIR;
}

void updateLight() {
  if (light_manualState == 1) {
    light_lightState = 1; 
  } else {
    light_lightState = (light_pirState == 1) ? 1 : 0;
  }
}

void applyLightState() {
  digitalWrite(_lightPin, light_lightState ? HIGH : LOW);
}

void printLightState() {
  Serial.print("Luce: ");
  Serial.println(light_lightState ? "ON" : "OFF");
}