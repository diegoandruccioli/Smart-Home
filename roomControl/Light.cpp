// Implementa il semplice controllo di una luce basata su sensore PIR e comando manuale di accensione
#include "Light.h" 
#include <Arduino.h>


// ----- Variabili globali e costanti -----
const int pinLed = 13;  // pin del led luce
int pirState = 0;       // stato del sensore PIR (movimento)
int lightState = 0;     // stato attuale luce (acceso/spento)
int manualState = 0;    // stato manuale (1=forza accensione)

// ----- Funzioni per gestione sensori e luce -----

// Simula aggiornamento sensori manuali e PIR (da chiamare ogni loop)
void updateSensorStates(int newManual, int newPIR) {
  manualState = newManual;
  pirState = newPIR;
}

// Calcola stato luce in base a sensori
void updateLight() {
  if (manualState == 1) {
    lightState = 1;  // luce forzata accesa da manuale
  } else {
    lightState = (pirState == 1) ? 1 : 0;  // luce accesa se PIR rileva movimento
  }
}

// Aggiorna fisicamente pin led (luce)
void applyLightState() {
  digitalWrite(pinLed, lightState ? HIGH : LOW);
}

// Stampa stato luce su seriale (debug)
void printLightState() {
  Serial.print("Luce: ");
  Serial.println(lightState ? "ON" : "OFF");
}

/*
// ----- Setup -----
void setup() {
  Serial.begin(9600);
  pinMode(pinLed, OUTPUT);
  Serial.println("Setup modulo luce completato");
}

// ----- Loop principale -----
void loop() {
  // Simuliamo cambio sensori (sostituire con lettura reale)
  int simulatedManual = digitalRead(12);  // es. pulsante manuale
  int simulatedPIR = digitalRead(14);     // es. sensore PIR

  updateSensorStates(simulatedManual, simulatedPIR);
  updateLight();
  applyLightState();
  printLightState();

  delay(1000);  // delay per simulazione
}

*/