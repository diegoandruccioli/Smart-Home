// Implementa il semplice controllo di una luce basata su sensore PIR e comando manuale di accensione
#include "Light.h" 
#include <Arduino.h>

// ----- Variabili globali e costanti -----
const int pinLed = 13;  // pin del led luce
// --- CORREZIONE: Nomi resi unici ---
int light_pirState = 0;       // stato del sensore PIR (movimento)
int light_lightState = 0;     // stato attuale luce (acceso/spento)
int light_manualState = 0;    // stato manuale (1=forza accensione)

// ----- Funzioni per gestione sensori e luce -----

// Simula aggiornamento sensori manuali e PIR (da chiamare ogni loop)
void updateSensorStates(int newManual, int newPIR) {
  // --- CORREZIONE: Aggiorna le variabili con nome unico ---
  light_manualState = newManual;
  light_pirState = newPIR;
}

// Calcola stato luce in base a sensori
void updateLight() {
  // --- CORREZIONE: Usa le variabili con nome unico ---
  if (light_manualState == 1) {
    light_lightState = 1;  // luce forzata accesa da manuale
  } else {
    light_lightState = (light_pirState == 1) ? 1 : 0;  // luce accesa se PIR rileva movimento
  }
}

// Aggiorna fisicamente pin led (luce)
void applyLightState() {
  // --- CORREZIONE: Usa le variabili con nome unico ---
  digitalWrite(pinLed, light_lightState ? HIGH : LOW);
}

// Stampa stato luce su seriale (debug)
void printLightState() {
  Serial.print("Luce: ");
  // --- CORREZIONE: Usa le variabili con nome unico ---
  Serial.println(light_lightState ? "ON" : "OFF");
}