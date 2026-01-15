#include "RollerShutter.h" 
#include <Arduino.h>
#include <ESP32Servo.h> 

Servo servo;
int roll_rollState = 0;
int roll_pirState = 0;
int roll_isDay = 0;
int roll_manualState = 0;

void updateRollState() {
  if (roll_manualState == 0) {
    // Logica Automatica
    if (roll_pirState == 1 && roll_isDay == 1) {
      roll_rollState = 100;
    } else if (roll_pirState == 0 && roll_isDay == 0) {
      roll_rollState = 0;
    }
  }
  
  if (servo.attached()) {
      int angle = map(roll_rollState, 0, 100, 0, 180);
      servo.write(angle);
  }
}

void handleMessage(String sensorName, long timestamp, int measure) {
  if (sensorName == "pir_sensor") {
    // Calcolo ora manuale dal timestamp
    long secondsInDay = timestamp % 86400;
    int currentHour = secondsInDay / 3600;
    roll_isDay = (currentHour >= 8 && currentHour < 19) ? 1 : 0;
    roll_pirState = measure;

  } else if (sensorName == "manual_roll") {
    roll_manualState = measure;
  } else if (sensorName == "roll") {
    if (roll_manualState == 1) {
        roll_rollState = measure;
    }
  }
}

void setupRoll(int pin) {
  servo.setPeriodHertz(50); 
  servo.attach(pin, 500, 2400);
}

void loopRoll(String sensorName, long timestamp, int measure) {
  handleMessage(sensorName, timestamp, measure);
  updateRollState();
}