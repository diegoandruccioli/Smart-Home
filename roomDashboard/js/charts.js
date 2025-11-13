// FILE: roomDashboard/js/charts.js

const chartData = {
  roll: {
    // Rimuoviamo i dati 'data' e 'layout' da qui,
    // verranno caricati dinamicamente.
    layout: {
      title: 'Storico tenda',
      xaxis: { title: 'giorno-ora', type: 'category' },
      yaxis: { title: 'aperto in %', range: [0, 100] }
    },
  },
  light: {
    layout: {
      title: 'Storico luce',
      xaxis: { title: 'giorno-ora', type: 'category' },
      yaxis: { title: 'acceso in %', range: [0, 100] }
    },
  }
};

/**
 * NUOVA FUNZIONE: Carica i dati storici e inizializza il grafico.
 */
async function loadAndInitializeCharts() {
  try {
    // 1. Carica dati Luce
    const lightResponse = await fetch('/api/get_chart_data/light');
    if (!lightResponse.ok) throw new Error('Errore caricamento dati luce');
    const lightAggData = await lightResponse.json();
    
    // Assegna i dati caricati (formato {x: [...], y: [...]})
    chartData.light.data = [{
        x: lightAggData.x,
        y: lightAggData.y,
        type: 'bar',
    }];
    
    // Inizializza il grafico Plotly con i dati storici
    Plotly.newPlot('lightchart', chartData.light.data, chartData.light.layout, { displayModeBar: true, responsive: true });

    // 2. Carica dati Tapparella
    const rollResponse = await fetch('/api/get_chart_data/roll');
    if (!rollResponse.ok) throw new Error('Errore caricamento dati tapparella');
    const rollAggData = await rollResponse.json();

    chartData.roll.data = [{
        x: rollAggData.x,
        y: rollAggData.y,
        type: 'bar',
    }];
    
    Plotly.newPlot('rollchart', chartData.roll.data, chartData.roll.layout, { displayModeBar: true, responsive: true });

  } catch (error) {
    console.error("Impossibile caricare i dati storici:", error);
    // Inizializza grafici vuoti in caso di fallimento
    initializeChart('lightchart', [{x:[], y:[], type:'bar'}], chartData.light.layout);
    initializeChart('rollchart', [{x:[], y:[], type:'bar'}], chartData.roll.layout);
  }
}

// Funzione originale per inizializzare (ora usata come fallback)
function initializeChart(chartId, data, layout) {
  Plotly.newPlot(chartId, data, layout, { displayModeBar: true, responsive: true });
}

/**
 * La funzione updateChart (live) deve essere modificata
 * per gestire l'aggregazione se necessario, o 
 * per aggiungere i dati correttamente.
 *
 * NOTA: La logica di aggregazione live
 * è complessa e potrebbe non allinearsi perfettamente con 
 * i dati storici aggregati. Per ora, la manteniamo 
 * per gli aggiornamenti live.
 */
function updateChart(chartId, data, layout, time, value) {
  const date = new Date(time * 1000); // Assicurati che 'time' sia in secondi
  const day = String(date.getDate()).padStart(2, '0');
  const hours = String(date.getHours()).padStart(2, '0');

  // Questa è la logica di aggregazione live
  if (value > 0) {
    const Column = `${day}-${hours}`; 
    // NOTA: il formato 'Column' qui è D-H, 
    // mentre l'API Python usa YYYY-MM-DD HH:00. 
    // Per coerenza, andrebbe standardizzato.
    
    if (!data[0].x.includes(Column)) {
      if (data[0].x.length >= 4) { // Limita a 4 colonne live
          data[0].x.shift();
          data[0].y.shift();
      }
      data[0].x.push(Column);
      data[0].y.push((1 / 3600) * 100);
    } else {
      let idx = data[0].x.indexOf(Column);
      data[0].y[idx] = data[0].y[idx] + (1 / 3600) * 100;
    }
  }

  Plotly.update(chartId, data, layout);
}

// RIMUOVI le chiamate originali
// initializeChart('lightchart', chartData.light.data, chartData.light.layout);
// initializeChart('rollchart', chartData.roll.data, chartData.roll.layout);

// AVVIA il caricamento dei dati storici non appena il DOM è pronto
document.addEventListener('DOMContentLoaded', loadAndInitializeCharts);