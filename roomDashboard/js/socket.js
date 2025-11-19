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

  // Aggiorna SOLO i controlli (icona luce, slider)
  updateDashboard(name, measure);
  
  // **CORREZIONE**: Forza il ricaricamento dei grafici al ricevimento di un nuovo dato (LIVE)
  // Il dato è ora salvato nel DB dal worker, quindi possiamo ricaricarlo.
  if (typeof loadAndInitializeCharts === 'function') {
      loadAndInitializeCharts();
  }
}

function sendMessage(message) {
// ... (Questa funzione rimane invariata)
  if (webSocket.readyState === WebSocket.OPEN) {
    webSocket.send(message);
    console.log('Messaggio inviato:', message);
    // **CORREZIONE**: Forza il ricaricamento dei grafici all'invio di un comando (IMMEDIATE)
    // Questo è il modo per vedere il proprio comando immediatamente sul grafico.
    if (typeof loadAndInitializeCharts === 'function') {
        loadAndInitializeCharts();
    }
  } else {
    console.warn('WebSocket non connesso. Impossibile inviare il messaggio:', message);
  }
}