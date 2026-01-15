/**
 * Funzione HELPER per creare un layout PULITO per Plotly.
 * I colori sono gestiti da style.css e dal tema.
 */
function getCleanChartLayout(title, yAxisTitle) {
  return {
    title: {
      text: title,
      font: { size: 16 },
      x: 0.05, // Allinea a sinistra
      xanchor: "left",
    },
    paper_bgcolor: "transparent", // Sfondo esterno trasparente
    plot_bgcolor: "transparent", // Sfondo interno trasparente
    font: {
      color: "var(--text-color)", // Colore dinamico da CSS
      family:
        'system-ui, -apple-system, "Segoe UI", Roboto, "Helvetica Neue", "Noto Sans", "Liberation Sans", Arial, sans-serif',
    },
    xaxis: {
      gridcolor: "var(--shadow-light)", // Colore griglia dinamico da CSS
      zeroline: false,
    },
    yaxis: {
      title: yAxisTitle,
      range: [0, 100],
      gridcolor: "var(--shadow-light)", // Colore griglia dinamico da CSS
      zeroline: false,
    },
    hovermode: "x unified",
    margin: { l: 40, r: 20, t: 40, b: 40 }, // Margini puliti
  };
}

/**
 * Funzione unica per caricare e (ri)disegnare i grafici.
 */
async function loadAndInitializeCharts() {
  try {
    console.log("Aggiornamento grafici storici (API)...");

    // 1. Carica dati Luce
    const lightResponse = await fetch("/api/get_chart_data/light");
    if (!lightResponse.ok) throw new Error("Errore caricamento dati luce");
    const lightAggData = await lightResponse.json();

    // --- USA GRAFICO AD AREA (SCATTER + FILL) ---
    const lightData = [
      {
        x: lightAggData.x,
        y: lightAggData.y,
        type: "scatter",
        mode: "lines",
        fill: "tozeroy",
        line: { color: "var(--primary-color)", width: 3 },
        fillcolor: "rgba(123, 97, 255, 0.1)", // Usa il colore primario con trasparenza
      },
    ];

    const lightLayout = getCleanChartLayout("Storico Luce", "% Utilizzo");
    Plotly.react("lightchart", lightData, lightLayout, {
      displayModeBar: false,
      responsive: true,
    });

    // 2. Carica dati TEMPERATURA
    const tempResponse = await fetch("/api/get_chart_data/temperature");
    if (!tempResponse.ok)
      throw new Error("Errore caricamento dati temperatura");
    const tempAggData = await tempResponse.json();

    // --- USA GRAFICO AD AREA (SCATTER + FILL) ---
    const tempData = [
      {
        x: tempAggData.x,
        y: tempAggData.y,
        type: "scatter",
        mode: "lines",
        fill: "tozeroy",
        line: { color: "#dc3545", width: 3 }, // Rosso
        fillcolor: "rgba(220, 53, 69, 0.1)", // Rosso con trasparenza
      },
    ];

    // Layout specifico per temperatura
    const tempLayout = getCleanChartLayout("Storico Temperatura", "°C");
    // Imposta range Y dinamico per temperatura (es. 10-35) o automatico
    tempLayout.yaxis.range = [10, 40];

    Plotly.react("rollchart", tempData, tempLayout, {
      displayModeBar: false,
      responsive: true,
    });
  } catch (error) {
    console.error("Impossibile caricare i dati storici:", error);
  }
}

// AVVIA il caricamento dei dati storici non appena il DOM è pronto
document.addEventListener("DOMContentLoaded", () => {
  // 1. Carica i dati subito
  loadAndInitializeCharts();

  // 2. Imposta un timer per ricaricare i dati ogni 60 secondi
  setInterval(loadAndInitializeCharts, 60000); // 1 minuto

  // 3. Aggiungi un listener per ridisegnare i grafici quando il tema cambia
  const themeButton = document.getElementById("theme-toggle-btn");
  if (themeButton) {
    themeButton.addEventListener("click", () => {
      // Ricarica i grafici dopo un breve ritardo per dare tempo al CSS di cambiare
      setTimeout(loadAndInitializeCharts, 50);
    });
  }
});
