
// ----------------------------- Tooltip ---------------------------
$('.tooltip').tooltip();
$(function () {
    $('[data-toggle="tooltip"]').tooltip()
})


// --- Canvas Data -------------------------------------------------
var time_data = $('#genres-time-pie').attr('values-y').split(', ');
var genres_data = $('#genres-time-pie').attr('values-x').split(', ');


// --- Create list of random color #45147e -------------------------
var rgb = [];
for(var j = 0; j < (genres_data.length); j++) {
    rgb.push('#'+Math.floor(Math.random()*16777215).toString(16));
}

// --- Bar graph: genres by times in hours -------------------------
var config = {
    type: 'bar',
    data: {
        datasets: [{
            data: time_data,
            backgroundColor: rgb,
        }],
        labels: genres_data
    },
    options: {
        tooltips: {
            enabled: false
        },
        hover: {
            animation: false,
            animationDuration: 0
        },
        animation: {
            duration: 1,
            onComplete: function () {
                var chartInstance = this.chart,
                ctx = chartInstance.ctx;
                ctx.font = Chart.helpers.fontString(Chart.defaults.global.defaultFontSize, Chart.defaults.global.defaultFontStyle, Chart.defaults.global.defaultFontFamily);                ctx.textAlign = 'center';
                ctx.textBaseline = 'bottom';

                this.data.datasets.forEach(function (dataset, i) {
                    var meta = chartInstance.controller.getDatasetMeta(i);
                    meta.data.forEach(function (bar, index) {
                        var data = dataset.data[index];
                        ctx.fillText(data, bar._model.x, bar._model.y - 5);
                    });
                });
            }
        },
        responsive: true,
        legend: {
            display: false
        },
        scales: {
            yAxes: [{
                type: 'linear',
                display: true,
                position: 'left',
                ticks: {
                    fontColor: '#e2e2e2',
                    fontSize: 18,
                    beginAtZero: true
                },
                gridLines: {
                    display: true,
                    color: 'rgba(127, 127, 127, 0.5)'
                },
            }],
            xAxes: [{
                ticks: {
                    fontColor: '#e2e2e2',
                    fontSize: 18,
                },
                gridLines: {
                    display: true,
                    color: 'rgba(127, 127, 127, 0.5)'
                },
            }]
        },
        title: {
            display: true,
            text: 'Time in hours by genres:',
            position: 'top',
            padding: 30,
            fontColor: '#e2e2e2',
            fontSize: 20,
            fontStyle: 'normal'
        },
    }
};
var ctx = document.getElementById('genres-time').getContext('2d');
var myPie = new Chart(ctx, config);
