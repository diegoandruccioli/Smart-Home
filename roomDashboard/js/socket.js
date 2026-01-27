// modifica url in base a ip del tuo computer che esegue il worker python
const webSocket = new WebSocket('ws://localhost:8080'); 

webSocket.onopen = function () {
  console.log('Socket attivo.');
};

webSocket.onerror = function (error) {
  console.error('Errore nella connessione WebSocket:', error);
};

webSocket.onmessage = function receiveMessage(event) {
  const data = JSON.parse(event.data);
  const measure = data.measure;
  const name = data.name;

  // aggiorna solo i controlli icona luce slider
  updateDashboard(name, measure);
}

function sendMessage(message) {
  if (webSocket.readyState === WebSocket.OPEN) {
    webSocket.send(message);
    console.log('messaggio inviato', message);
  } else {
    console.warn('websocket non connesso impossibile inviare il messaggio', message);
  }
}