/**
 * js/dashboard.js
 * Logica UI: Temperatura e Luce
 */

// --- ELEMENTI DOM ---
const lightCheckManual = document.getElementById("lightcheck");
const btnToggleLight = document.getElementById("btn-toggle-light");
const lightSwitchHidden = document.getElementById("lightswitch");
const lightIcon = document.getElementById("light-icon");
const lightLabel = document.getElementById("light-label");

// Nuovo elemento per visualizzare i gradi
const tempDisplay = document.getElementById("temp-display");

// --- HELPER ---
function createJson(obj, value) {
  const json = { name: obj, measure: value };
  return JSON.stringify(json);
}

// --- 1. GESTIONE LUCE (INVARIATA) ---
lightCheckManual.addEventListener("click", () => {
    const isManual = lightCheckManual.checked;
    btnToggleLight.disabled = !isManual;
    sendMessage(createJson("manual_light", isManual ? 1 : 0));
});

btnToggleLight.addEventListener("click", () => {
    lightSwitchHidden.checked = !lightSwitchHidden.checked;
    handleLightChange();
});

function handleLightChange() {
    const isOn = lightSwitchHidden.checked;
    sendMessage(createJson("light", isOn ? 1 : 0));
    updateLightUI(isOn);
}

function updateLightUI(isOn) {
    lightSwitchHidden.checked = isOn;
    if (isOn) {
        lightIcon.classList.remove("bi-lightbulb-off");
        lightIcon.classList.add("bi-lightbulb-fill", "text-warning"); // Giallo quando acceso
        lightLabel.textContent = "Acceso";
        lightLabel.classList.remove("text-muted");
        lightLabel.classList.add("text-primary");
    } else {
        lightIcon.classList.remove("bi-lightbulb-fill", "text-warning");
        lightIcon.classList.add("bi-lightbulb-off", "text-muted");
        lightLabel.textContent = "Spento";
        lightLabel.classList.add("text-muted");
        lightLabel.classList.remove("text-primary");
    }
}

// --- 2. RICEZIONE DATI DAL SERVER ---
// Questa funzione viene chiamata da socket.js quando arriva un messaggio MQTT
function updateDashboard(name, value) {
    
    // A. Aggiornamento Temperatura
    if (name == "temperature") {
        // Arrotonda a 1 cifra decimale
        const tempVal = parseFloat(value).toFixed(1);
        if (tempDisplay) {
            tempDisplay.textContent = tempVal;
            
            // (Opzionale) Cambia colore se sopra soglia AC (24 gradi)
            if (parseFloat(value) > 24.0) {
                tempDisplay.classList.add("text-danger");
                tempDisplay.classList.remove("text-primary");
            } else {
                tempDisplay.classList.add("text-primary");
                tempDisplay.classList.remove("text-danger");
            }
        }
    }
    
    // B. Aggiornamento Stato Luce (Feedback)
    else if (name == "light") {
        const isOn = (value == 1 || value == "1" || value == true);
        updateLightUI(isOn);
    }
}