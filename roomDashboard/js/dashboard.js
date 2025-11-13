/**
 * Questo file gestisce la logica dei CONTROLLI.
 * Ascolta i click sui pulsanti/slider (input dell'utente) e invia
 * i comandi al server tramite WebSocket.
 * * Gestisce anche l'aggiornamento VISIVO dei controlli (l'icona della luce,
 * la posizione dello slider) quando riceve dati live dal server.
 */

// --- 1. Selezione degli Elementi DOM ---
// Questi ID provengono da index.html

// Controlli "Manuale"
const lightButton = document.getElementById("lightcheck");
const rollButton = document.getElementById("rollcheck");

// Controllo Luce
const lightswitch = document.getElementById("lightswitch"); // L'input checkbox nascosto
const lightbulbIcon = document.getElementById("icon"); // L'icona <i> nel pulsante grande
const lightLabel = document.getElementById('light-label'); // L'etichetta "Acceso/Spento"
const lightHeroButton = document.querySelector('.light-control-hero'); // Il pulsante-icona cliccabile

// Controllo Tapparella
const range = document.getElementById('rollrange');
const valueSpan = document.getElementById('rollvalue');

// Disabilita i controlli all'avvio (la modalità automatica è predefinita)
lightswitch.disabled = true;
range.disabled = true;


// --- 2. Funzione di Aggiornamento (chiamata da socket.js) ---

/**
 * Aggiorna l'interfaccia (i controlli) in base ai messaggi
 * ricevuti in tempo reale dal server (via WebSocket).
 * @param {string} name - Il nome del controllo (es. "light", "roll")
 * @param {any} value - Il nuovo valore (es. 1, 0, 50)
 */
function updateDashboard(name, value) {
  
  // Aggiornamento LUCE
  if (name == "light") {
    const isChecked = value > 0;
    lightswitch.checked = isChecked;
    
    if (isChecked) {
      // Se acceso: usa l'icona 'bi-lightbulb' (piena) e aggiorna l'etichetta
      lightbulbIcon.classList.replace("bi-lightbulb-off", "bi-lightbulb");
      if (lightLabel) lightLabel.textContent = "Acceso";
    } else {
      // Se spento: usa l'icona 'bi-lightbulb-off' e aggiorna l'etichetta
      lightbulbIcon.classList.replace("bi-lightbulb", "bi-lightbulb-off");
      if (lightLabel) lightLabel.textContent = "Spento";
    }
  } 
  
  // Aggiornamento TAPPARELLA
  else if (name == "roll") {
    // Aggiorna il testo del badge
    valueSpan.textContent = `${value}`;
    
    // Muove il badge lungo lo slider per seguire il pallino
    // (Questa logica calcola la posizione percentuale)
    const offset = ((value - range.min + 2) / (range.max - range.min + 4)) * range.offsetWidth;
    valueSpan.style.transform = `translateX(${offset}px) translateY(-120%)`;
    
    // Aggiorna la posizione del pallino dello slider
    range.value = value;
  }
}


// --- 3. Funzione Helper per creare JSON ---
function createJson(obj, value) {
  const json = {
    name: obj,
    measure: value,
  }
  return JSON.stringify(json);
}


// --- 4. Event Listener (al caricamento della pagina) ---
document.addEventListener('DOMContentLoaded', () => {

  // --- Evento per il Pulsante-Icona della LUCE ---
  if (lightHeroButton) {
      lightHeroButton.addEventListener('click', () => {
          // Se lo switch è disabilitato (modalità automatica), non fa nulla
          if (lightswitch.disabled) return;
          
          // Altrimenti, simula un "click" sullo switch checkbox nascosto
          // Questo fa scattare l'evento 'lightswitch.addEventListener("click", ...)' qui sotto
          lightswitch.click();
      });
  }

  // --- Evento per lo switch "Manuale" della LUCE ---
  lightButton.addEventListener("click", () => {
    // Abilita/Disabilita lo switch principale
    lightswitch.disabled = !lightButton.checked;
    
    // Invia lo stato (manuale/automatico) al server
    sendMessage(createJson("manual_light", lightButton.checked ? 1 : 0));
  });
  
  // --- Evento per lo switch (nascosto) della LUCE ---
  lightswitch.addEventListener("click", () => {
    const isChecked = lightswitch.checked;
    // Invia il comando (acceso/spento) al server
    sendMessage(createJson("light", isChecked ? 1 : 0));
    
    // Aggiorna la grafica (lo fa anche updateDashboard, ma questo è più reattivo)
    if (isChecked) {
      lightbulbIcon.classList.replace("bi-lightbulb-off", "bi-lightbulb");
      if (lightLabel) lightLabel.textContent = "Acceso";
    } else {
      lightbulbIcon.classList.replace("bi-lightbulb", "bi-lightbulb-off");
      if (lightLabel) lightLabel.textContent = "Spento";
    }
  });


  // --- Evento per lo switch "Manuale" della TAPPARELLA ---
  rollButton.addEventListener("click", () => {
    // Abilita/Disabilita lo slider
    range.disabled = !rollButton.checked;
    
    // Invia lo stato (manuale/automatico) al server
    sendMessage(createJson("manual_roll", rollButton.checked ? 1 : 0));
  });

  // --- Evento per lo slider della TAPPARELLA ---
  range.addEventListener('input', (event) => {
    const value = event.target.value;
    
    // Invia il comando (posizione 0-100) al server
    sendMessage(createJson("roll", value));
    
    // Aggiorna il testo e la posizione del badge
    valueSpan.textContent = `${value}`;
    const offset = ((value - range.min + 2) / (range.max - range.min + 4)) * range.offsetWidth;
    valueSpan.style.transform = `translateX(${offset}px) translateY(-120%)`;
  });
  
});