#include "RollerShutter.h" 
#include <Arduino.h>
#include <ESP32Servo.h>
// Variabili globali
Servo servo;
int roll_rollState = 0;
int roll_pirState = 0;
int roll_isDay = 0;
int roll_manualState = 0;

void updateRollState() {
  if (roll_manualState == 0) {
    // Logica Automatica: Apre se c'è movimento (PIR=1) E se è giorno (isDay=1)
    if (roll_pirState == 1 && roll_isDay == 1) {
      roll_rollState = 100;
    } else if (roll_pirState == 0 && roll_isDay == 0) {
      roll_rollState = 0;
    }
  }
  // Muove il servo (0-100% mappato su 0-180 gradi)
  int angle = map(roll_rollState, 0, 100, 0, 180);
  servo.write(angle);
}

void handleMessage(String sensorName, long timestamp, int measure) {
  if (sensorName == "pir_sensor") {
    
    // --- CALCOLO MANUALE DELL'ORA (Senza TimeLib) ---
    // Il timestamp è in secondi totali.
    // 1. Prendiamo il resto della divisione per 86400 (secondi in un giorno) -> Secondi passati da mezzanotte
    // 2. Dividiamo per 3600 (secondi in un'ora) -> Otteniamo l'ora attuale (0-23)
    long secondsInDay = timestamp % 86400;
    int currentHour = secondsInDay / 3600;

    // Imposta "Giorno" se l'ora è tra le 8 e le 19
    roll_isDay = (currentHour >= 8 && currentHour < 19) ? 1 : 0;
    
    // Aggiorna stato PIR
    roll_pirState = measure;

  } else if (sensorName == "manual_roll") {
    roll_manualState = measure;
  } else if (sensorName == "roll") {
    roll_rollState = measure;
  }
}

void setupRoll(int pin) {
  servo.attach(pin);
}

void loopRoll(String sensorName, long timestamp, int measure) {
  handleMessage(sensorName, timestamp, measure);
  updateRollState();
}