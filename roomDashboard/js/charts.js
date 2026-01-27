//gestione grafico temperatura
 
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
      color: '#333333',
      family: 'system-ui, sans-serif'
    },
    xaxis: { 
      gridcolor: '#e5e5e5',
      zeroline: false,
    },
    yaxis: { 
      title: yAxisTitle, 
      gridcolor: '#e5e5e5',
      zeroline: false,
    },
    hovermode: 'x unified',
    margin: { l: 40, r: 20, t: 40, b: 40 }
  };
}

async function loadAndInitializeCharts() {
  try {
    console.log("Aggiornamento grafico Temperatura...");
    
    const tempResponse = await fetch('/api/get_chart_data/temperature');
    if (!tempResponse.ok) throw new Error('Errore dati temperatura');
    const tempAggData = await tempResponse.json();
    
    const tempData = [{
        x: tempAggData.x,
        y: tempAggData.y,
        type: 'scatter',
        mode: 'lines',
        fill: 'tozeroy', 
        line: { color: '#ff5722', width: 3 }, 
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
    setInterval(loadAndInitializeCharts, 60000); // aggiorna ogni minuto
});