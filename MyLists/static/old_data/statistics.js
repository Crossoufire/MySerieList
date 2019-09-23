var ctx = document.getElementById('myChart').getContext('2d');
var myChart = new Chart(ctx, {
    type: 'bar',
    data: {
        labels: {{ x_abs|safe }},
        datasets: [{
            label: 'Series watched',
            data: {{ y_abs }},
            backgroundColor: [
                'rgba(185, 75, 100, 0.7)',
                'rgba(185, 75, 100, 0.7)',
                'rgba(185, 75, 100, 0.7)',
                'rgba(185, 75, 100, 0.7)',
                'rgba(185, 75, 100, 0.7)',
                'rgba(185, 75, 100, 0.7)',
                'rgba(185, 75, 100, 0.7)',
                'rgba(185, 75, 100, 0.7)',
                'rgba(185, 75, 100, 0.7)',
                'rgba(185, 75, 100, 0.7)'
            ],
            borderColor: [
                'rgba(23, 23, 23, 0.8)',
                'rgba(23, 23, 23, 0.8)',
                'rgba(23, 23, 23, 0.8)',
                'rgba(23, 23, 23, 0.8)',
                'rgba(23, 23, 23, 0.8)',
                'rgba(23, 23, 23, 0.8)',
                'rgba(23, 23, 23, 0.8)',
                'rgba(23, 23, 23, 0.8)',
                'rgba(23, 23, 23, 0.8)',
                'rgba(23, 23, 23, 0.8)'
            ],
            borderWidth: 2
        }]
    },
    options: {
        legend: {
            labels: {
                fontColor: "#CCC",
            }
        },
        scales: {
            yAxes: [{
                ticks: {
                    beginAtZero: true,
                    fontColor: "#CCC"
                },
                gridLines: {
                    display: true,
					drawBorder: true,
                    color: "rgba(255, 255, 255, 0.2)"
                }
            }],
            xAxes: [{
                ticks: {
                    fontColor: "#CCC",
                },
                gridLines: {
                    display: true,
					drawBorder: true,
                    color: "rgba(255, 255, 255, 0.2)",
                }
            }],
        }
    }
});


var ctx = document.getElementById('myChart2').getContext('2d');
var myChart = new Chart(ctx, {
    type: 'bar',
    data: {
        labels: {{ x_abs|safe }},
        datasets: [{
            label: 'Time watched',
            data: {{ y_abs_2 }},
            backgroundColor: [
                'rgba(185, 75, 100, 0.7)',
                'rgba(185, 75, 100, 0.7)',
                'rgba(185, 75, 100, 0.7)',
                'rgba(185, 75, 100, 0.7)',
                'rgba(185, 75, 100, 0.7)',
                'rgba(185, 75, 100, 0.7)',
                'rgba(185, 75, 100, 0.7)',
                'rgba(185, 75, 100, 0.7)',
                'rgba(185, 75, 100, 0.7)',
                'rgba(185, 75, 100, 0.7)'
            ],
            borderColor: [
                'rgba(23, 23, 23, 0.8)',
                'rgba(23, 23, 23, 0.8)',
                'rgba(23, 23, 23, 0.8)',
                'rgba(23, 23, 23, 0.8)',
                'rgba(23, 23, 23, 0.8)',
                'rgba(23, 23, 23, 0.8)',
                'rgba(23, 23, 23, 0.8)',
                'rgba(23, 23, 23, 0.8)',
                'rgba(23, 23, 23, 0.8)',
                'rgba(23, 23, 23, 0.8)'
            ],
            borderWidth: 2
        }]
    },
    options: {
        legend: {
            labels: {
                fontColor: "#CCC",
            }
        },
        scales: {
            yAxes: [{
                ticks: {
                    beginAtZero: true,
                    fontColor: "#CCC"
                },
                gridLines: {
                    display: true,
					drawBorder: true,
                    color: "rgba(255, 255, 255, 0.2)"
                }
            }],
            xAxes: [{
                ticks: {
                    fontColor: "#CCC",
                },
                gridLines: {
                    display: true,
					drawBorder: true,
                    color: "rgba(255, 255, 255, 0.2)",
                }
            }],
        }
    }
});


var ctx = document.getElementById('myChart3').getContext('2d');
var myChart = new Chart(ctx, {
    type: 'bar',
    data: {
        labels: {{ x_abs|safe }},
        datasets: [{
            label: 'Episodes watched',
            data: {{ y_abs_3 }},
            backgroundColor: [
                'rgba(185, 75, 100, 0.7)',
                'rgba(185, 75, 100, 0.7)',
                'rgba(185, 75, 100, 0.7)',
                'rgba(185, 75, 100, 0.7)',
                'rgba(185, 75, 100, 0.7)',
                'rgba(185, 75, 100, 0.7)',
                'rgba(185, 75, 100, 0.7)',
                'rgba(185, 75, 100, 0.7)',
                'rgba(185, 75, 100, 0.7)',
                'rgba(185, 75, 100, 0.7)'
            ],
            borderColor: [
                'rgba(23, 23, 23, 0.8)',
                'rgba(23, 23, 23, 0.8)',
                'rgba(23, 23, 23, 0.8)',
                'rgba(23, 23, 23, 0.8)',
                'rgba(23, 23, 23, 0.8)',
                'rgba(23, 23, 23, 0.8)',
                'rgba(23, 23, 23, 0.8)',
                'rgba(23, 23, 23, 0.8)',
                'rgba(23, 23, 23, 0.8)',
                'rgba(23, 23, 23, 0.8)'
            ],
            borderWidth: 2
        }]
    },
    options: {
        legend: {
            labels: {
                fontColor: "#CCC",
            }
        },
        scales: {
            yAxes: [{
                ticks: {
                    beginAtZero: true,
                    fontColor: "#CCC"
                },
                gridLines: {
                    display: true,
					drawBorder: true,
                    color: "rgba(255, 255, 255, 0.2)"
                }
            }],
            xAxes: [{
                ticks: {
                    fontColor: "#CCC",
                },
                gridLines: {
                    display: true,
					drawBorder: true,
                    color: "rgba(255, 255, 255, 0.2)",
                }
            }],
        }
    }
});