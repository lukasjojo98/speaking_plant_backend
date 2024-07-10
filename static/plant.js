function createChart() {
  // Chart.register(...Chart.registerables);

  const labels = ["1", "2", "3", "4", "5", "6", "7"];
  const data1 = {
    labels: labels,
    datasets: [{
      label: 'Nährstoff',
      data: [65, 59, 80, 81, 56, 55, 40],
      fill: false,
      borderColor: 'rgb(75, 192, 192)',
      tension: 0.1
    }]
  };

  const data2 = {
    labels: labels,
    datasets: [{
      label: 'Feuchtigkeit',
      data: [65, 20, 40, 81, 10, 20, 40],
      fill: false,
      borderColor: 'rgb(0, 255, 0)',
      tension: 0.1
    }]
  };

  const data3 = {
    labels: labels,
    datasets: [{
      label: 'Licht',
      data: [20, 50, 40, 50, 80, 50, 30],
      fill: false,
      borderColor: 'rgb(255, 255, 0)',
      tension: 0.1
    }]
  };

  new Chart(document.getElementById('chart-1'), {
    type: 'line',
    data: data1,
  });

  new Chart(document.getElementById('chart-2'), {
    type: 'line',
    data: data2,
  });

  new Chart(document.getElementById('chart-3'), {
    type: 'line',
    data: data3,
  });
}

// Call the createChart function after the DOM has fully loaded
document.addEventListener('DOMContentLoaded', function() {
  createChart();
});
