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
  // Rimuoviamo il log qui per pulire la console
  // console.log(data); 
  const measure = data.measure;
  const name = data.name;

  // --- INIZIO MODIFICA ---
  //
  // const namechart = name + "chart";
  //
  // NON aggiornare il grafico qui. Ci pensa il polling dell'API.
  // updateChart(namechart, chartData[name].data, chartData[name].layout, data.timestamp, data.measure);
  //
  // --- FINE MODIFICA ---

  // Aggiorna SOLO i controlli (icona luce, slider)
  updateDashboard(name, measure);
}

function sendMessage(message) {
// ... (Questa funzione rimane invariata)
  if (webSocket.readyState === WebSocket.OPEN) {
    webSocket.send(message);
    console.log('Messaggio inviato:', message);
  } else {
    console.warn('WebSocket non connesso. Impossibile inviare il messaggio:', message);
  }
}