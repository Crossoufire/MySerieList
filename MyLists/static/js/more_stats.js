

// --- Series Canvas Data -------------------------------------------------
let series_episodes_labels = $('#episodes-series-bar').attr('values-y').split(', ');
let series_episodes_data = $('#episodes-series-bar').attr('values-x').split(', ');
series_episodes_labels.pop(-1);
series_episodes_data.pop(-1);

let series_episodes_rgb = [];
for(let j = 0; j < (series_episodes_data.length); j++) {
    series_episodes_rgb.push('#'+Math.floor(Math.random()*16777215).toString(16));
}

let series_episodes_config = {
    type: 'horizontalBar',
    data: {
        labels: series_episodes_labels,
        datasets: [{
            data: series_episodes_data,
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
                var chartInstance = this.chart,
                ctx = chartInstance.ctx;
                ctx.textAlign = 'left';
                ctx.textBaseline = 'top';

                this.data.datasets.forEach(function (dataset, i) {
                    var meta = chartInstance.controller.getDatasetMeta(i);
                    meta.data.forEach(function (bar, index) {
                        var data = dataset.data[index];
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
let series_episodes_ctx = document.getElementById('episodes-series').getContext('2d');
let series_episodes_bar = new Chart(series_episodes_ctx, series_episodes_config);

let series_periods_labels = $('#periods-series-bar').attr('values-y').split(', ');
let series_periods_data = $('#periods-series-bar').attr('values-x').split(', ');
series_periods_labels.pop(-1);
series_periods_data.pop(-1);

let series_periods_rgb = [];
for(let j = 0; j < (series_periods_data.length); j++) {
    series_periods_rgb.push('#'+Math.floor(Math.random()*16777215).toString(16));
}

let series_periods_config = {
    type: 'horizontalBar',
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
                var chartInstance = this.chart,
                ctx = chartInstance.ctx;
                ctx.textAlign = 'left';
                ctx.textBaseline = 'top';

                this.data.datasets.forEach(function (dataset, i) {
                    var meta = chartInstance.controller.getDatasetMeta(i);
                    meta.data.forEach(function (bar, index) {
                        var data = dataset.data[index];
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
let series_periods_ctx = document.getElementById('periods-series').getContext('2d');
let series_periods_bar = new Chart(series_periods_ctx, series_periods_config);

let series_genres_labels = $('#genres-series-bar').attr('values-y').split(', ');
let series_genres_data = $('#genres-series-bar').attr('values-x').split(', ');
series_genres_labels.pop(-1);
series_genres_data.pop(-1);

let series_genres_rgb = [];
for(let j = 0; j < (series_genres_data.length); j++) {
    series_genres_rgb.push('#'+Math.floor(Math.random()*16777215).toString(16));
}

let series_genres_config = {
    type: 'horizontalBar',
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
                var chartInstance = this.chart,
                ctx = chartInstance.ctx;
                ctx.textAlign = 'left';
                ctx.textBaseline = 'top';

                this.data.datasets.forEach(function (dataset, i) {
                    var meta = chartInstance.controller.getDatasetMeta(i);
                    meta.data.forEach(function (bar, index) {
                        var data = dataset.data[index];
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
let series_genres_ctx = document.getElementById('genres-series').getContext('2d');
let series_genres_bar = new Chart(series_genres_ctx, series_genres_config);


// --- Anime Canvas Data -------------------------------------------------
let anime_episodes_labels = $('#episodes-anime-bar').attr('values-y').split(', ');
let anime_episodes_data = $('#episodes-anime-bar').attr('values-x').split(', ');
anime_episodes_labels.pop(-1);
anime_episodes_data.pop(-1);

let anime_episodes_rgb = [];
for(let j = 0; j < (anime_episodes_data.length); j++) {
    anime_episodes_rgb.push('#'+Math.floor(Math.random()*16777215).toString(16));
}

let anime_episodes_config = {
    type: 'horizontalBar',
    data: {
        labels: anime_episodes_labels,
        datasets: [{
            data: anime_episodes_data,
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
                var chartInstance = this.chart,
                ctx = chartInstance.ctx;
                ctx.textAlign = 'left';
                ctx.textBaseline = 'top';

                this.data.datasets.forEach(function (dataset, i) {
                    var meta = chartInstance.controller.getDatasetMeta(i);
                    meta.data.forEach(function (bar, index) {
                        var data = dataset.data[index];
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
let anime_episodes_ctx = document.getElementById('episodes-anime').getContext('2d');
let anime_episodes_bar = new Chart(anime_episodes_ctx, anime_episodes_config);

let anime_periods_labels = $('#periods-anime-bar').attr('values-y').split(', ');
let anime_periods_data = $('#periods-anime-bar').attr('values-x').split(', ');
anime_periods_labels.pop(-1);
anime_periods_data.pop(-1);

let anime_periods_rgb = [];
for(let j = 0; j < (anime_periods_data.length); j++) {
    anime_periods_rgb.push('#'+Math.floor(Math.random()*16777215).toString(16));
}

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
                var chartInstance = this.chart,
                ctx = chartInstance.ctx;
                ctx.textAlign = 'left';
                ctx.textBaseline = 'top';

                this.data.datasets.forEach(function (dataset, i) {
                    var meta = chartInstance.controller.getDatasetMeta(i);
                    meta.data.forEach(function (bar, index) {
                        var data = dataset.data[index];
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
let anime_periods_ctx = document.getElementById('periods-anime').getContext('2d');
let anime_periods_bar = new Chart(anime_periods_ctx, anime_periods_config);

let anime_genres_labels = $('#genres-anime-bar').attr('values-y').split(', ');
let anime_genres_data = $('#genres-anime-bar').attr('values-x').split(', ');
anime_genres_labels.pop(-1);
anime_genres_data.pop(-1);

let anime_genres_rgb = [];
for(let j = 0; j < (anime_genres_data.length); j++) {
    anime_genres_rgb.push('#'+Math.floor(Math.random()*16777215).toString(16));
}

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
                var chartInstance = this.chart,
                ctx = chartInstance.ctx;
                ctx.textAlign = 'left';
                ctx.textBaseline = 'top';

                this.data.datasets.forEach(function (dataset, i) {
                    var meta = chartInstance.controller.getDatasetMeta(i);
                    meta.data.forEach(function (bar, index) {
                        var data = dataset.data[index];
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
let anime_genres_ctx = document.getElementById('genres-anime').getContext('2d');
let anime_genres_bar = new Chart(anime_genres_ctx, anime_genres_config);


// --- Movies Canvas Data -------------------------------------------------
let movies_lengths_labels = $('#lengths-movies-bar').attr('values-y').split(', ');
let movies_lengths_data = $('#lengths-movies-bar').attr('values-x').split(', ');
movies_lengths_labels.pop(-1);
movies_lengths_data.pop(-1);

let movies_lengths_rgb = [];
for(let j = 0; j < (movies_lengths_data.length); j++) {
    movies_lengths_rgb.push('#'+Math.floor(Math.random()*16777215).toString(16));
}

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
                var chartInstance = this.chart,
                ctx = chartInstance.ctx;
                ctx.textAlign = 'left';
                ctx.textBaseline = 'top';

                this.data.datasets.forEach(function (dataset, i) {
                    var meta = chartInstance.controller.getDatasetMeta(i);
                    meta.data.forEach(function (bar, index) {
                        var data = dataset.data[index];
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
let movies_lengths_ctx = document.getElementById('lengths-movies').getContext('2d');
let movies_lengths_bar = new Chart(movies_lengths_ctx, movies_lengths_config);

let movies_periods_labels = $('#periods-movies-bar').attr('values-y').split(', ');
let movies_periods_data = $('#periods-movies-bar').attr('values-x').split(', ');
movies_periods_labels.pop(-1);
movies_periods_data.pop(-1);

let movies_periods_rgb = [];
for(let j = 0; j < (movies_periods_data.length); j++) {
    movies_periods_rgb.push('#'+Math.floor(Math.random()*16777215).toString(16));
}

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
                var chartInstance = this.chart,
                ctx = chartInstance.ctx;
                ctx.textAlign = 'left';
                ctx.textBaseline = 'top';

                this.data.datasets.forEach(function (dataset, i) {
                    var meta = chartInstance.controller.getDatasetMeta(i);
                    meta.data.forEach(function (bar, index) {
                        var data = dataset.data[index];
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
let movies_periods_ctx = document.getElementById('periods-movies').getContext('2d');
let movies_periods_bar = new Chart(movies_periods_ctx, movies_periods_config);

let movies_genres_labels = $('#genres-movies-bar').attr('values-y').split(', ');
let movies_genres_data = $('#genres-movies-bar').attr('values-x').split(', ');
movies_genres_labels.pop(-1);
movies_genres_data.pop(-1);

let movies_genres_rgb = [];
for(let j = 0; j < (movies_genres_data.length); j++) {
    movies_genres_rgb.push('#'+Math.floor(Math.random()*16777215).toString(16));
}

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
                var chartInstance = this.chart,
                ctx = chartInstance.ctx;
                ctx.textAlign = 'left';
                ctx.textBaseline = 'top';

                this.data.datasets.forEach(function (dataset, i) {
                    var meta = chartInstance.controller.getDatasetMeta(i);
                    meta.data.forEach(function (bar, index) {
                        var data = dataset.data[index];
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
let movies_genres_ctx = document.getElementById('genres-movies').getContext('2d');
let movies_genres_bar = new Chart(movies_genres_ctx, movies_genres_config);


// --- Media genres container size -------------------------------------------------
let series_height = 40*series_genres_data.length + 'px';
let anime_height = 40*anime_genres_data.length + 'px';
let movies_height = 40*movies_genres_data.length + 'px';

$('.series-genres-container').attr('style', 'height:' +series_height+';');
$('.anime-genres-container').attr('style', 'height:' +anime_height+';');
$('.movies-genres-container').attr('style', 'height:' +movies_height+';');
