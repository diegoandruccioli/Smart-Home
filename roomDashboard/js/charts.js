/**
 * js/charts.js
 * Gestione Grafico Temperatura
 */

function getCleanChartLayout(title, yAxisTitle) {
  return {
    title: {
        text: title,
        font: { size: 16 },
        x: 0.05,
        xanchor: 'left',
    },
    paper_bgcolor: 'transparent',
    plot_bgcolor: 'transparent',
    font: {
      color: 'var(--text-color)',
      family: 'system-ui, sans-serif'
    },
    xaxis: { 
      gridcolor: 'var(--shadow-light)',
      zeroline: false,
    },
    yaxis: { 
      title: yAxisTitle, 
      // Rimuovo il range fisso 0-100 per la temperatura, lascio automatico o setto un range verosimile
      // range: [0, 50], 
      gridcolor: 'var(--shadow-light)',
      zeroline: false,
    },
    hovermode: 'x unified',
    margin: { l: 40, r: 20, t: 40, b: 40 }
  };
}

async function loadAndInitializeCharts() {
  try {
    console.log("Aggiornamento grafico Temperatura...");
    
    // 1. Richiedi dati 'temperature' al posto di 'light'
    const tempResponse = await fetch('/api/get_chart_data/temperature');
    if (!tempResponse.ok) throw new Error('Errore dati temperatura');
    const tempAggData = await tempResponse.json();
    
    // Configurazione Grafico Linea Rossa/Arancione
    const tempData = [{
        x: tempAggData.x,
        y: tempAggData.y,
        type: 'scatter',
        mode: 'lines',
        fill: 'tozeroy', 
        line: { color: '#ff5722', width: 3 }, // Colore Caldo
        fillcolor: 'rgba(255, 87, 34, 0.1)',
        name: 'Temperatura'
    }];
    
    const tempLayout = getCleanChartLayout('Storico Temperatura', 'Gradi (°C)');
    Plotly.react('tempchart', tempData, tempLayout, { displayModeBar: false, responsive: true });

  } catch (error) {
    console.error("Impossibile caricare i dati storici:", error);
  }
}

document.addEventListener('DOMContentLoaded', () => {
    loadAndInitializeCharts();
    setInterval(loadAndInitializeCharts, 60000); // Aggiorna ogni minuto
    
    const themeButton = document.getElementById('theme-toggle-btn');
    if (themeButton) {
        themeButton.addEventListener('click', () => {
            setTimeout(loadAndInitializeCharts, 50);
        });
    }
});