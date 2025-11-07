// Modifica l'URL in base all'IP del tuo computer che esegue il worker Python
const webSocket = new WebSocket('ws://localhost:8080'); 

webSocket.onopen = function () {
  console.log('Socket attivo.');
};

webSocket.onerror = function (error) {
  console.error('Errore nella connessione WebSocket:', error);
};

webSocket.onmessage = function receiveMessage(event) {
  const data = JSON.parse(event.data);
  console.log(data);
  const measure = data.measure;
  const name = data.name;
  const namechart = name + "chart";
  // La funzione updateChart deve gestire i dati di "light", "roll", "pir" e "ldr"
  updateChart(namechart, chartData[name].data, chartData[name].layout, data.timestamp, data.measure);
  updateDashboard(name, measure);
}

function sendMessage(message) {
  // Controlla se il socket è pronto prima di inviare
  if (webSocket.readyState === WebSocket.OPEN) {
    webSocket.send(message);
    console.log('Messaggio inviato:', message);
  } else {
    console.warn('WebSocket non connesso. Impossibile inviare il messaggio:', message);
  }
}
