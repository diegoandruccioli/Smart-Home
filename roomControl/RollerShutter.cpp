#include "RollerShutter.h" 
#include <Arduino.h>
#include <Servo.h>
#include <TimeLib.h>  // per gestione ora sistema


// Variabili globali / stato 
Servo servo;          // libreria per 'servomotore' 
int rollState = 0;    // stato tapparella (0-100%)
int pirState = 0;     // stato sensore PIR (0/1)
int isDay = 0;        // giorno attivo (1 se tra ore 8 e 19)
int manualState = 0;  // stato manuale (1=forza chiusura/apertura)

// Imposta tempo sistema da timestamp esterno
void setTimeFromTimestamp(long timestamp) {
  setTime(timestamp); // funzione TimeLib
}

// Aggiorna stato in base a input sensori e orario
void updateRollState() {
  if (manualState == 0) {
    if (pirState == 1 && isDay == 1) {
      rollState = 100;
    } else if (pirState == 0 && isDay == 0) {
      rollState = 0;
    }
  }
  int angle = map(rollState, 0, 100, 0, 180);
  servo.write(angle);
}

// Gestisce messaggi JSON in input per aggiornare stato sensori
void handleMessage(String sensorName, long timestamp, int measure) {
  if (sensorName == "pir_sensor") {
    setTimeFromTimestamp(timestamp);
    pirState = measure;
    int currentHour = hour();
    isDay = (currentHour >= 8 && currentHour < 19) ? 1 : 0;
  } else if (sensorName == "manual_roll") {
    manualState = measure;
  } else if (sensorName == "roll") {
    rollState = measure;
  }
}

// Setup iniziale (attacca servo a pin)
void setupRoll(int pin) {
  servo.attach(pin);
}

// Loop simulato: processa update e aggiorna servo
void loopRoll(String sensorName, long timestamp, int measure) {
  handleMessage(sensorName, timestamp, measure);
  updateRollState();
}