/**
 * GESTIONE INTERFACCIA E COMANDI
 */

// --- SELEZIONE ELEMENTI DOM ---
const lightCheckManual = document.getElementById("lightcheck");
const rollCheckManual = document.getElementById("rollcheck");

// Elementi Luce
const btnToggleLight = document.getElementById("btn-toggle-light");
const lightSwitchHidden = document.getElementById("lightswitch");
const lightIcon = document.getElementById("light-icon");
const lightLabel = document.getElementById("light-label");

// Elementi Tapparella (MODIFICATO)
const rollValueDisplay = document.getElementById("rollvalue");
const rollButtons = document.querySelectorAll(".roll-btn"); // Seleziona tutti i pulsanti %

// --- FUNZIONE HELPER JSON ---
function createJson(obj, value) {
  const json = { name: obj, measure: value };
  return JSON.stringify(json);
}


// --- 1. GESTIONE LUCE ---
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
        lightIcon.classList.remove("bi-lightbulb-off-fill", "text-muted");
        lightIcon.classList.add("bi-lightbulb-fill", "light-on");
        lightLabel.textContent = "Acceso";
        lightLabel.classList.remove("text-muted");
        lightLabel.classList.add("text-primary");
    } else {
        lightIcon.classList.remove("bi-lightbulb-fill", "light-on");
        lightIcon.classList.add("bi-lightbulb-off-fill", "text-muted");
        lightLabel.textContent = "Spento";
        lightLabel.classList.add("text-muted");
        lightLabel.classList.remove("text-primary");
    }
}


// --- 2. GESTIONE TAPPARELLA (MODIFICATA) ---

// A. Cambio Modalità Manuale/Automatico
rollCheckManual.addEventListener("click", () => {
    const isManual = rollCheckManual.checked;
    
    // Abilita/Disabilita TUTTI i pulsanti della tapparella
    rollButtons.forEach(btn => {
        btn.disabled = !isManual;
    });
    
    // Invia stato al server
    sendMessage(createJson("manual_roll", isManual ? 1 : 0));
});

// B. Click sui pulsanti Preset (0%, 25%, ecc.)
rollButtons.forEach(btn => {
    btn.addEventListener("click", (e) => {
        // Recupera il valore dall'attributo data-value (es. "50")
        const val = e.target.getAttribute("data-value");
        
        // Aggiorna UI locale
        updateRollUI(val);
        
        // Invia comando al server
        sendMessage(createJson("roll", val));
    });
});

// Funzione dedicata per aggiornare la grafica della tapparella
function updateRollUI(value) {
    // 1. Aggiorna il testo
    rollValueDisplay.textContent = `${value}%`;
    
    // 2. Aggiorna lo stato "attivo" dei pulsanti
    rollButtons.forEach(btn => {
        // Rimuove la classe active da tutti
        btn.classList.remove("active", "btn-primary", "text-white");
        btn.classList.add("btn-outline-secondary");
        
        // Aggiunge la classe active solo se il valore corrisponde
        if (btn.getAttribute("data-value") == value) {
            btn.classList.remove("btn-outline-secondary");
            btn.classList.add("active", "btn-primary", "text-white");
        }
    });
}


// --- 3. RICEZIONE DATI DAL SERVER ---
function updateDashboard(name, value) {
    
    if (name == "light") {
        const isOn = (value == 1 || value == "1" || value == true);
        updateLightUI(isOn);
    }
    
    else if (name == "roll") {
        // Converte in intero per sicurezza
        const intValue = parseInt(value);
        
        // Trova il pulsante più vicino o esatto (per gestire valori intermedi se arrivano dai sensori)
        // Qui facciamo un aggiornamento diretto
        updateRollUI(intValue);
    }
}
