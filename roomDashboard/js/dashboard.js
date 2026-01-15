/**
 * js/dashboard.js
 * Logica UI: Temperatura, Luce e Buzzer
 */

// --- ELEMENTI DOM ---
const lightCheckManual = document.getElementById("lightcheck"); // Interruttore Generale Manuale

// Luce
const btnToggleLight = document.getElementById("btn-toggle-light");
const lightSwitchHidden = document.getElementById("lightswitch");
const lightIcon = document.getElementById("light-icon");
const lightLabel = document.getElementById("light-label");

// Buzzer
const btnToggleBuzzer = document.getElementById("btn-toggle-buzzer");
const buzzerSwitchHidden = document.getElementById("buzzerswitch");
const buzzerIcon = document.getElementById("buzzer-icon");
const buzzerLabel = document.getElementById("buzzer-label");

// Temperatura
const tempDisplay = document.getElementById("temp-display");

// --- HELPER ---
function createJson(obj, value) {
  const json = { name: obj, measure: value };
  return JSON.stringify(json);
}

// --- 1. GESTIONE MANUAL MODE (Generale) ---
lightCheckManual.addEventListener("click", () => {
    const isManual = lightCheckManual.checked;
    
    // Abilita/Disabilita i pulsanti
    btnToggleLight.disabled = !isManual;
    btnToggleBuzzer.disabled = !isManual; // Ora controlla anche il buzzer
    
    // Invia comando al server per dire che siamo in manuale (lato Luce)
    sendMessage(createJson("manual_light", isManual ? 1 : 0));
});

// --- 2. GESTIONE LUCE ---
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
        lightIcon.className = "bi bi-lightbulb-fill text-warning";
        lightLabel.textContent = "Acceso";
        lightLabel.className = "text-primary";
    } else {
        lightIcon.className = "bi bi-lightbulb-off text-muted";
        lightLabel.textContent = "Spento";
        lightLabel.className = "text-muted";
    }
}

// --- 3. GESTIONE BUZZER ---
btnToggleBuzzer.addEventListener("click", () => {
    buzzerSwitchHidden.checked = !buzzerSwitchHidden.checked;
    handleBuzzerChange();
});

function handleBuzzerChange() {
    const isOn = buzzerSwitchHidden.checked;
    // Inviamo "buzzer" al server, che lo tradurrà in temperatura fake
    sendMessage(createJson("buzzer", isOn ? 1 : 0));
    updateBuzzerUI(isOn);
}

function updateBuzzerUI(isOn) {
    buzzerSwitchHidden.checked = isOn;
    if (isOn) {
        buzzerIcon.className = "bi bi-volume-up-fill text-danger"; // Icona attiva
        buzzerLabel.textContent = "Attivo";
        buzzerLabel.className = "text-danger";
    } else {
        buzzerIcon.className = "bi bi-volume-mute text-muted";
        buzzerLabel.textContent = "Spento";
        buzzerLabel.className = "text-muted";
    }
}

// --- 4. RICEZIONE DATI DAL SERVER ---
function updateDashboard(name, value) {
    
    // A. Aggiornamento Temperatura
    if (name == "temperature") {
        const floatVal = parseFloat(value);
        const tempVal = floatVal.toFixed(1);
        
        if (tempDisplay) {
            tempDisplay.textContent = tempVal;
            
            // Logica colore temperatura
            if (floatVal > 24.0) {
                tempDisplay.classList.add("text-danger");
                tempDisplay.classList.remove("text-primary");
                
                // Feedback visuale implicito: se la temp è alta, il buzzer è acceso
                updateBuzzerUI(true);
            } else {
                tempDisplay.classList.add("text-primary");
                tempDisplay.classList.remove("text-danger");
                
                // Feedback visuale implicito: se la temp è bassa, il buzzer è spento
                updateBuzzerUI(false);
            }
        }
    }
    
    // B. Aggiornamento Stato Luce
    else if (name == "light") {
        const isOn = (value == 1 || value == "1" || value == true);
        updateLightUI(isOn);
    }
}