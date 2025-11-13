#include "RollerShutter.h" 
#include <Arduino.h>
#include <Servo.h>
#include <TimeLib.h>  // per gestione ora sistema


// Variabili globali / stato 
Servo servo;          // libreria per 'servomotore' 
// --- CORREZIONE: Nomi resi unici ---
int roll_rollState = 0;    // stato tapparella (0-100%)
int roll_pirState = 0;     // stato sensore PIR (0/1)
int roll_isDay = 0;        // giorno attivo (1 se tra ore 8 e 19)
int roll_manualState = 0;  // stato manuale (1=forza chiusura/apertura)

// Imposta tempo sistema da timestamp esterno
void setTimeFromTimestamp(long timestamp) {
  setTime(timestamp); // funzione TimeLib
}

// Aggiorna stato in base a input sensori e orario
void updateRollState() {
  // --- CORREZIONE: Usa le variabili con nome unico ---
  if (roll_manualState == 0) {
    if (roll_pirState == 1 && roll_isDay == 1) {
      roll_rollState = 100;
    } else if (roll_pirState == 0 && roll_isDay == 0) {
      roll_rollState = 0;
    }
  }
  int angle = map(roll_rollState, 0, 100, 0, 180);
  servo.write(angle);
}

// Gestisce messaggi JSON in input per aggiornare stato sensori
void handleMessage(String sensorName, long timestamp, int measure) {
  // --- CORREZIONE: Usa le variabili con nome unico ---
  if (sensorName == "pir_sensor") {
    setTimeFromTimestamp(timestamp);
    roll_pirState = measure;
    int currentHour = hour();
    roll_isDay = (currentHour >= 8 && currentHour < 19) ? 1 : 0;
  } else if (sensorName == "manual_roll") {
    roll_manualState = measure;
  } else if (sensorName == "roll") {
    roll_rollState = measure;
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