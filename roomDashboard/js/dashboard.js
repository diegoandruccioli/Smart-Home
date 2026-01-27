/**
 * js dashboard js
 * logica ui temperatura luce e buzzer
 */

// elementi dom
const lightCheckManual = document.getElementById("lightcheck"); // interruttore generale manuale

// luce
const btnToggleLight = document.getElementById("btn-toggle-light");
const lightSwitchHidden = document.getElementById("lightswitch");
const lightIcon = document.getElementById("light-icon");
const lightLabel = document.getElementById("light-label");

// buzzer
const btnToggleBuzzer = document.getElementById("btn-toggle-buzzer");
const buzzerSwitchHidden = document.getElementById("buzzerswitch");
const buzzerIcon = document.getElementById("buzzer-icon");
const buzzerLabel = document.getElementById("buzzer-label");

// temperatura
const tempDisplay = document.getElementById("temp-display");

// helper
function createJson(obj, value) {
  const json = { name: obj, measure: value };
  return JSON.stringify(json);
}

// gestione manual mode generale
lightCheckManual.addEventListener("click", () => {
    const isManual = lightCheckManual.checked;
    
    // abilita disabilita i pulsanti
    btnToggleLight.disabled = !isManual;
    btnToggleBuzzer.disabled = !isManual; // ora controlla anche il buzzer
    
    // invia comando al server per dire che siamo in manuale lato luce
    sendMessage(createJson("manual_light", isManual ? 1 : 0));
});

// gestione luce
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

// gestione buzzer
btnToggleBuzzer.addEventListener("click", () => {
    buzzerSwitchHidden.checked = !buzzerSwitchHidden.checked;
    handleBuzzerChange();
});

function handleBuzzerChange() {
    const isOn = buzzerSwitchHidden.checked;
    // inviamo buzzer al server che lo tradurra in temperatura fake
    sendMessage(createJson("buzzer", isOn ? 1 : 0));
    updateBuzzerUI(isOn);
}

function updateBuzzerUI(isOn) {
    buzzerSwitchHidden.checked = isOn;
    if (isOn) {
        buzzerIcon.className = "bi bi-volume-up-fill text-danger"; // icona attiva
        buzzerLabel.textContent = "Attivo";
        buzzerLabel.className = "text-danger";
    } else {
        buzzerIcon.className = "bi bi-volume-mute text-muted";
        buzzerLabel.textContent = "Spento";
        buzzerLabel.className = "text-muted";
    }
}

// ricezione dati dal server
function updateDashboard(name, value) {
    
    // aggiornamento temperatura
    if (name == "temperature") {
        const floatVal = parseFloat(value);
        const tempVal = floatVal.toFixed(1);
        
        if (tempDisplay) {
            tempDisplay.textContent = tempVal;
            
            // logica colore temperatura
            if (floatVal > 24.0) {
                tempDisplay.classList.add("text-danger");
                tempDisplay.classList.remove("text-primary");
                
                // feedback visuale implicito se la temp e alta il buzzer e acceso
                updateBuzzerUI(true);
            } else {
                tempDisplay.classList.add("text-primary");
                tempDisplay.classList.remove("text-danger");
                
                // feedback visuale implicito se la temp e bassa il buzzer e spento
                updateBuzzerUI(false);
            }
        }
    }
    
    // aggiornamento stato luce
    else if (name == "light") {
        const isOn = (value == 1 || value == "1" || value == true);
        updateLightUI(isOn);
    }
}