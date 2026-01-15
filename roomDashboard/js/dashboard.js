/**
 * Questo file gestisce la logica dei CONTROLLI.
 * Ascolta i click sui pulsanti/slider (input dell'utente) e invia
 * i comandi al server tramite WebSocket.
 * * Gestisce anche l'aggiornamento VISIVO dei controlli (l'icona della luce,
 * la posizione dello slider) quando riceve dati live dal server.
 */

// --- 1. Selezione degli Elementi DOM ---
// Questi ID provengono da index.html

// --- 2. GESTIONE CONDIZIONATORE (Nuovo) ---
const acCheckManual = document.getElementById("accheck");
const btnToggleAc = document.getElementById("btn-toggle-ac");
const acSwitchHidden = document.getElementById("acswitch");
const acIcon = document.getElementById("ac-icon");
const acLabel = document.getElementById("ac-label");

// --- Funzione di Aggiornamento UI AC ---
function updateAcUI(isOn) {
  acSwitchHidden.checked = isOn;
  if (isOn) {
    acIcon.classList.remove("text-muted");
    acIcon.classList.add("text-primary", "ac-on");
    acLabel.textContent = "Acceso";
    acLabel.classList.remove("text-muted");
    acLabel.classList.add("text-primary");
  } else {
    acIcon.classList.remove("text-primary", "ac-on");
    acIcon.classList.add("text-muted");
    acLabel.textContent = "Spento";
    acLabel.classList.add("text-muted");
    acLabel.classList.remove("text-primary");
  }
}

// --- Funzione Principale Update (chiamata dal socket) ---
function updateDashboard(name, value) {
  if (name == "light") {
    const isChecked = value > 0;
    lightswitch.checked = isChecked;
    if (isChecked) {
      lightbulbIcon.classList.replace("bi-lightbulb-off", "bi-lightbulb");
      if (lightLabel) lightLabel.textContent = "Acceso";
    } else {
      lightbulbIcon.classList.replace("bi-lightbulb", "bi-lightbulb-off");
      if (lightLabel) lightLabel.textContent = "Spento";
    }
  } else if (name == "ac") {
    const isOn = value == 1 || value == "1" || value == true;
    updateAcUI(isOn);
  }
}

// --- Funzione Helper per creare JSON ---
function createJson(obj, value) {
  const json = { name: obj, measure: value };
  return JSON.stringify(json);
}

// --- Event Listener ---
// --- Event Listener ---
document.addEventListener("DOMContentLoaded", () => {
  // --- LUCE ---
  const lightCheckManual = document.getElementById("lightcheck");
  const btnToggleLight = document.getElementById("btn-toggle-light");
  const lightSwitchHidden = document.getElementById("lightswitch");
  const lightHeroButton = document.querySelector(".light-control-hero");
  const lightbulbIcon = document.getElementById("icon");
  const lightLabel = document.getElementById("light-label");

  // 1. Switch Manuale Luce
  if (lightCheckManual) {
    lightCheckManual.addEventListener("click", () => {
      const isManual = lightCheckManual.checked;

      // Abilita/Disabilita controlli
      lightSwitchHidden.disabled = !isManual;
      if (btnToggleLight) btnToggleLight.disabled = !isManual;

      // Invia comando al server
      sendMessage(createJson("manual_light", isManual ? 1 : 0));
    });
  }

  // 2. Click Icona Grande (Hero) Luce
  if (lightHeroButton) {
    lightHeroButton.addEventListener("click", () => {
      if (lightSwitchHidden.disabled) return;
      lightSwitchHidden.click();
    });
  }

  // 3. Click Pulsante "Cambia Stato" Luce
  if (btnToggleLight) {
    btnToggleLight.addEventListener("click", () => {
      if (lightSwitchHidden.disabled) return; // Doppio controllo
      lightSwitchHidden.click();
    });
  }

  // 4. Change effettivo (Checkbox Nascosto) Luce
  if (lightSwitchHidden) {
    lightSwitchHidden.addEventListener("click", () => {
      const isChecked = lightSwitchHidden.checked;
      sendMessage(createJson("light", isChecked ? 1 : 0));

      // Aggiorna UI locale
      if (isChecked) {
        lightbulbIcon.classList.replace("bi-lightbulb-off", "bi-lightbulb");
        if (lightLabel) lightLabel.textContent = "Acceso";
      } else {
        lightbulbIcon.classList.replace("bi-lightbulb", "bi-lightbulb-off");
        if (lightLabel) lightLabel.textContent = "Spento";
      }
    });
  }

  // --- CONDIZIONATORE ---

  // 1. Switch Manuale AC
  if (acCheckManual) {
    acCheckManual.addEventListener("click", () => {
      const isManual = acCheckManual.checked;
      btnToggleAc.disabled = !isManual; // Abilita/Disabilita pulsante
      sendMessage(createJson("manual_ac", isManual ? 1 : 0));
    });
  }

  // 2. Pulsante Toggle AC
  if (btnToggleAc) {
    btnToggleAc.addEventListener("click", () => {
      acSwitchHidden.checked = !acSwitchHidden.checked;
      handleAcChange();
    });
  }

  function handleAcChange() {
    const isOn = acSwitchHidden.checked;
    sendMessage(createJson("ac", isOn ? 1 : 0));
    updateAcUI(isOn);
  }
});
