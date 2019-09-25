//radar
var ctxR = document.getElementById("radarChart").getContext('2d');
var myRadarChart = new Chart(ctxR, {
  type: 'radar',
  data: {
    labels: ["QB", "RB", "WR", "TE", "FLX", "DEF", "K"],
    datasets: [{
        label: "Team 1",
        data: [40, 50, 60, 15, 20, 15, 10],
        backgroundColor: [
          'rgba(105, 0, 132, .2)',
        ],
        borderColor: [
          'rgba(200, 99, 132, .7)',
        ],
        borderWidth: 2
      },
      {
        label: "Team 2",
        data: [35, 30, 75, 25, 15, 20, 5],
        backgroundColor: [
          'rgba(0, 250, 220, .2)',
        ],
        borderColor: [
          'rgba(0, 213, 132, .7)',
        ],
        borderWidth: 2
      }
    ]
  },
  options: {
    responsive: true
  }
});