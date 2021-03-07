

// --- Series Canvas Data ----------------------------------------------------------------------------------------
let series_eps_labels = $('#eps-series-bar').attr('values-y').split(', ');
let series_eps_data = $('#eps-series-bar').attr('values-x').split(', ');
series_eps_labels.pop();
series_eps_data.pop();

let series_eps_config = {
    type: 'bar',
    data: {
        labels: series_eps_labels,
        datasets: [{
            data: series_eps_data,
            backgroundColor: '#216e7d',
        }],
    },
    options: {
        events: false,
        responsive: true,
        maintainAspectRatio: false,
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
                let chartInstance = this.chart,
                ctx = chartInstance.ctx;
                ctx.textAlign = 'center';
                ctx.textBaseline = 'bottom';

                this.data.datasets.forEach(function (dataset, i) {
                    let meta = chartInstance.controller.getDatasetMeta(i);
                    meta.data.forEach(function (bar, index) {
                        let data = dataset.data[index];
                        ctx.fillText(data, bar._model.x, bar._model.y);
                    });
                });
            }
        },
        legend: {
            display: false
        },
        scales: {
            yAxes: [{
                ticks: {
                    fontColor: '#e2e2e2',
                    fontSize: 18,
                },
                gridLines: {
                    display: false,
                    color: 'rgba(127, 127, 127, 0.4)',
                },
            }],
            xAxes: [{
                display: true,
                position: 'bottom',
                ticks: {
                    fontColor: '#e2e2e2',
                    fontSize: 18,
                },
                gridLines: {
                    display: false,
                    color: 'rgba(127, 127, 127, 0.4)',
                },
            }]
        },
        title: {
            display: true,
            fontColor: '#e2e2e2',
            fontSize: 16,
        },
    }
};
new Chart(document.getElementById('eps-series').getContext('2d'), series_eps_config);

let series_periods_labels = $('#periods-series-bar').attr('values-y').split(', ');
let series_periods_data = $('#periods-series-bar').attr('values-x').split(', ');
series_periods_labels.pop();
series_periods_data.pop();

let series_periods_config = {
    type: 'bar',
    data: {
        labels: series_periods_labels,
        datasets: [{
            data: series_periods_data,
            backgroundColor: '#216e7d',
        }],
    },
    options: {
        events: false,
        responsive: true,
        maintainAspectRatio: false,
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
                let chartInstance = this.chart,
                ctx = chartInstance.ctx;
                ctx.textAlign = 'center';
                ctx.textBaseline = 'bottom';

                this.data.datasets.forEach(function (dataset, i) {
                    let meta = chartInstance.controller.getDatasetMeta(i);
                    meta.data.forEach(function (bar, index) {
                        let data = dataset.data[index];
                        ctx.fillText(data, bar._model.x, bar._model.y);
                    });
                });
            }
        },
        legend: {
            display: false
        },
        scales: {
            yAxes: [{
                ticks: {
                    fontColor: '#e2e2e2',
                    fontSize: 18,
                },
                gridLines: {
                    display: false,
                    color: 'rgba(127, 127, 127, 0.4)',
                },
            }],
            xAxes: [{
                display: true,
                position: 'bottom',
                ticks: {
                    fontColor: '#e2e2e2',
                    fontSize: 12,
                },
                gridLines: {
                    display: false,
                    color: 'rgba(127, 127, 127, 0.4)',
                },
            }]
        },
        title: {
            display: true,
            fontColor: '#e2e2e2',
            fontSize: 16,
        },
    }
};
new Chart(document.getElementById('periods-series').getContext('2d'), series_periods_config);

let series_genres_labels = $('#genres-series-bar').attr('values-y').split(', ');
let series_genres_data = $('#genres-series-bar').attr('values-x').split(', ');
series_genres_labels.pop();
series_genres_data.pop();

let series_genres_config = {
    type: 'bar',
    data: {
        labels: series_genres_labels,
        datasets: [{
            data: series_genres_data,
            backgroundColor: '#216e7d',
        }],
    },
    options: {
        events: false,
        responsive: true,
        maintainAspectRatio: false,
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
                let chartInstance = this.chart,
                ctx = chartInstance.ctx;
                ctx.textAlign = 'center';
                ctx.textBaseline = 'bottom';

                this.data.datasets.forEach(function (dataset, i) {
                    let meta = chartInstance.controller.getDatasetMeta(i);
                    meta.data.forEach(function (bar, index) {
                        let data = dataset.data[index];
                        ctx.fillText(data + ' h', bar._model.x, bar._model.y);
                    });
                });
            }
        },
        legend: {
            display: false
        },
        scales: {
            yAxes: [{
                ticks: {
                    fontColor: '#e2e2e2',
                    fontSize: 18,
                },
                gridLines: {
                    display: false,
                    color: 'rgba(127, 127, 127, 0.4)',
                },
            }],
            xAxes: [{
                display: true,
                position: 'bottom',
                ticks: {
                    fontColor: '#e2e2e2',
                    fontSize: 16,
                }
            }]
        },
        title: {
            display: true,
            fontColor: '#e2e2e2',
            fontSize: 16,
        },
    }
};
new Chart(document.getElementById('genres-series').getContext('2d'), series_genres_config);


// --- Anime Canvas Data -----------------------------------------------------------------------------------------
let anime_eps_labels = $('#eps-anime-bar').attr('values-y').split(', ');
let anime_eps_data = $('#eps-anime-bar').attr('values-x').split(', ');
anime_eps_labels.pop();
anime_eps_data.pop();

let anime_episodes_config = {
    type: 'horizontalBar',
    data: {
        labels: anime_eps_labels,
        datasets: [{
            data: anime_eps_data,
            backgroundColor: '#945141',
        }],
    },
    options: {
        events: false,
        responsive: true,
        maintainAspectRatio: false,
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
                let chartInstance = this.chart,
                ctx = chartInstance.ctx;
                ctx.textAlign = 'left';
                ctx.textBaseline = 'top';

                this.data.datasets.forEach(function (dataset, i) {
                    let meta = chartInstance.controller.getDatasetMeta(i);
                    meta.data.forEach(function (bar, index) {
                        let data = dataset.data[index];
                        ctx.fillText(data, bar._model.x + 10, bar._model.y - 7);
                    });
                });
            }
        },
        legend: {
            display: false
        },
        scales: {
            yAxes: [{
                ticks: {
                    fontColor: '#e2e2e2',
                    fontSize: 18,
                },
                gridLines: {
                    display: false,
                    color: 'rgba(127, 127, 127, 0.4)',
                },
            }],
            xAxes: [{
                display: true,
                position: 'top',
                ticks: {
                    fontColor: '#e2e2e2',
                    fontSize: 18,
                },
                gridLines: {
                    display: false,
                    color: 'rgba(127, 127, 127, 0.4)',
                },
            }]
        },
        title: {
            display: true,
            fontColor: '#e2e2e2',
            fontSize: 16,
        },
    }
};
new Chart(document.getElementById('eps-anime').getContext('2d'), anime_episodes_config);

let anime_periods_labels = $('#periods-anime-bar').attr('values-y').split(', ');
let anime_periods_data = $('#periods-anime-bar').attr('values-x').split(', ');
anime_periods_labels.pop();
anime_periods_data.pop();

let anime_periods_config = {
    type: 'horizontalBar',
    data: {
        labels: anime_periods_labels,
        datasets: [{
            data: anime_periods_data,
            backgroundColor: '#945141',
        }],
    },
    options: {
        events: false,
        responsive: true,
        maintainAspectRatio: false,
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
                let chartInstance = this.chart,
                ctx = chartInstance.ctx;
                ctx.textAlign = 'left';
                ctx.textBaseline = 'top';

                this.data.datasets.forEach(function (dataset, i) {
                    let meta = chartInstance.controller.getDatasetMeta(i);
                    meta.data.forEach(function (bar, index) {
                        let data = dataset.data[index];
                        ctx.fillText(data, bar._model.x + 10, bar._model.y - 7);
                    });
                });
            }
        },
        legend: {
            display: false
        },
        scales: {
            yAxes: [{
                ticks: {
                    fontColor: '#e2e2e2',
                    fontSize: 18,
                },
                gridLines: {
                    display: false,
                    color: 'rgba(127, 127, 127, 0.4)',
                },
            }],
            xAxes: [{
                display: true,
                position: 'top',
                ticks: {
                    fontColor: '#e2e2e2',
                    fontSize: 18,
                },
                gridLines: {
                    display: false,
                    color: 'rgba(127, 127, 127, 0.4)',
                },
            }]
        },
        title: {
            display: true,
            fontColor: '#e2e2e2',
            fontSize: 16,
        },
    }
};
new Chart(document.getElementById('periods-anime').getContext('2d'), anime_periods_config);

let anime_genres_labels = $('#genres-anime-bar').attr('values-y').split(', ');
let anime_genres_data = $('#genres-anime-bar').attr('values-x').split(', ');
anime_genres_labels.pop();
anime_genres_data.pop();

let anime_genres_config = {
    type: 'horizontalBar',
    data: {
        labels: anime_genres_labels,
        datasets: [{
            data: anime_genres_data,
            backgroundColor: '#945141',
        }],
    },
    options: {
        events: false,
        responsive: true,
        maintainAspectRatio: false,
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
                let chartInstance = this.chart,
                ctx = chartInstance.ctx;
                ctx.textAlign = 'left';
                ctx.textBaseline = 'top';

                this.data.datasets.forEach(function (dataset, i) {
                    let meta = chartInstance.controller.getDatasetMeta(i);
                    meta.data.forEach(function (bar, index) {
                        let data = dataset.data[index];
                        ctx.fillText(data + ' h', bar._model.x + 10, bar._model.y - 7);
                    });
                });
            }
        },
        legend: {
            display: false
        },
        scales: {
            yAxes: [{
                ticks: {
                    fontColor: '#e2e2e2',
                    fontSize: 18,
                },
                gridLines: {
                    display: false,
                    color: 'rgba(127, 127, 127, 0.4)',
                },
            }],
            xAxes: [{
                display: true,
                position: 'top',
                ticks: {
                    fontColor: '#e2e2e2',
                    fontSize: 18,
                },
                gridLines: {
                    display: false,
                    color: 'rgba(127, 127, 127, 0.4)',
                },
            }]
        },
        title: {
            display: true,
            fontColor: '#e2e2e2',
            fontSize: 16,
        },
    }
};
new Chart(document.getElementById('genres-anime').getContext('2d'), anime_genres_config);


// --- Movies Canvas Data ---------------------------------------------------------------------------------------
let movies_lengths_labels = $('#lengths-movies-bar').attr('values-y').split(', ');
let movies_lengths_data = $('#lengths-movies-bar').attr('values-x').split(', ');
movies_lengths_labels.pop();
movies_lengths_data.pop();

let movies_lengths_config = {
    type: 'horizontalBar',
    data: {
        labels: movies_lengths_labels,
        datasets: [{
            data: movies_lengths_data,
            backgroundColor: '#8c7821',
        }],
    },
    options: {
        events: false,
        responsive: true,
        maintainAspectRatio: false,
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
                let chartInstance = this.chart,
                ctx = chartInstance.ctx;
                ctx.textAlign = 'left';
                ctx.textBaseline = 'top';

                this.data.datasets.forEach(function (dataset, i) {
                    let meta = chartInstance.controller.getDatasetMeta(i);
                    meta.data.forEach(function (bar, index) {
                        let data = dataset.data[index];
                        ctx.fillText(data, bar._model.x + 10, bar._model.y - 7);
                    });
                });
            }
        },
        legend: {
            display: false
        },
        scales: {
            yAxes: [{
                ticks: {
                    fontColor: '#e2e2e2',
                    fontSize: 18,
                },
                gridLines: {
                    display: false,
                    color: 'rgba(127, 127, 127, 0.4)',
                },
            }],
            xAxes: [{
                display: true,
                position: 'top',
                ticks: {
                    fontColor: '#e2e2e2',
                    fontSize: 18,
                },
                gridLines: {
                    display: false,
                    color: 'rgba(127, 127, 127, 0.4)',
                },
            }]
        },
        title: {
            display: true,
            fontColor: '#e2e2e2',
            fontSize: 16,
        },
    }
};
new Chart(document.getElementById('lengths-movies').getContext('2d'), movies_lengths_config);

let movies_periods_labels = $('#periods-movies-bar').attr('values-y').split(', ');
let movies_periods_data = $('#periods-movies-bar').attr('values-x').split(', ');
movies_periods_labels.pop();
movies_periods_data.pop();

let movies_periods_config = {
    type: 'horizontalBar',
    data: {
        labels: movies_periods_labels,
        datasets: [{
            data: movies_periods_data,
            backgroundColor: '#8c7821',
        }],
    },
    options: {
        events: false,
        responsive: true,
        maintainAspectRatio: false,
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
                let chartInstance = this.chart,
                ctx = chartInstance.ctx;
                ctx.textAlign = 'left';
                ctx.textBaseline = 'top';

                this.data.datasets.forEach(function (dataset, i) {
                    let meta = chartInstance.controller.getDatasetMeta(i);
                    meta.data.forEach(function (bar, index) {
                        let data = dataset.data[index];
                        ctx.fillText(data, bar._model.x + 10, bar._model.y - 7);
                    });
                });
            }
        },
        legend: {
            display: false
        },
        scales: {
            yAxes: [{
                ticks: {
                    fontColor: '#e2e2e2',
                    fontSize: 18,
                },
                gridLines: {
                    display: false,
                    color: 'rgba(127, 127, 127, 0.4)',
                },
            }],
            xAxes: [{
                display: true,
                position: 'top',
                ticks: {
                    fontColor: '#e2e2e2',
                    fontSize: 18,
                },
                gridLines: {
                    display: false,
                    color: 'rgba(127, 127, 127, 0.4)',
                },
            }]
        },
        title: {
            display: true,
            fontColor: '#e2e2e2',
            fontSize: 16,
        },
    }
};
new Chart(document.getElementById('periods-movies').getContext('2d'), movies_periods_config);

let movies_genres_labels = $('#genres-movies-bar').attr('values-y').split(', ');
let movies_genres_data = $('#genres-movies-bar').attr('values-x').split(', ');
movies_genres_labels.pop();
movies_genres_data.pop();

let movies_genres_config = {
    type: 'horizontalBar',
    data: {
        labels: movies_genres_labels,
        datasets: [{
            data: movies_genres_data,
            backgroundColor: '#8c7821',
        }],
    },
    options: {
        events: false,
        responsive: true,
        maintainAspectRatio: false,
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
                let chartInstance = this.chart,
                ctx = chartInstance.ctx;
                ctx.textAlign = 'left';
                ctx.textBaseline = 'top';

                this.data.datasets.forEach(function (dataset, i) {
                    let meta = chartInstance.controller.getDatasetMeta(i);
                    meta.data.forEach(function (bar, index) {
                        let data = dataset.data[index];
                        ctx.fillText(data + ' h', bar._model.x + 10, bar._model.y - 7);
                    });
                });
            }
        },
        legend: {
            display: false
        },
        scales: {
            yAxes: [{
                ticks: {
                    fontColor: '#e2e2e2',
                    fontSize: 18,
                },
                gridLines: {
                    display: false,
                    color: 'rgba(127, 127, 127, 0.4)',
                },
            }],
            xAxes: [{
                display: true,
                position: 'top',
                ticks: {
                    fontColor: '#e2e2e2',
                    fontSize: 18,
                },
                gridLines: {
                    display: false,
                    color: 'rgba(127, 127, 127, 0.4)',
                },
            }]
        },
        title: {
            display: true,
            fontColor: '#e2e2e2',
            fontSize: 16,
        },
    }
};
new Chart(document.getElementById('genres-movies').getContext('2d'), movies_genres_config);


// --- Media genres container size -------------------------------------------------------------------------------
let series_height = 40*series_genres_data.length + 'px';
let anime_height = 40*anime_genres_data.length + 'px';
let movies_height = 40*movies_genres_data.length + 'px';

$('.series-genres-container').attr('style', 'height:' +series_height+';');
$('.anime-genres-container').attr('style', 'height:' +anime_height+';');
$('.movies-genres-container').attr('style', 'height:' +movies_height+';');
