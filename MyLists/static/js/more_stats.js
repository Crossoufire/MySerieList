
// --- Movies Canvas Data ---------------------------------------------------------------------------------
let movies_lengths_labels = $('#lengths-movies-bar').attr('values-y').split(', ');
let movies_lengths_data = $('#lengths-movies-bar').attr('values-x').split(', ');
movies_lengths_labels.pop();
movies_lengths_data.pop();

let movies_lengths_config = {
    type: 'bar',
    data: {
        labels: movies_lengths_labels,
        datasets: [{
            data: movies_lengths_data,
            backgroundColor: [
                'rgba(255, 99, 132, 0.8)',
                'rgba(255, 159, 64, 0.8)',
                'rgba(255, 205, 86, 0.8)',
                'rgba(75, 192, 192, 0.8)',
                'rgba(54, 162, 235, 0.8)',
                'rgba(153, 102, 255, 0.8)'
            ],
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

                this.data.datasets.forEach(function (dataset, i) {
                    let meta = chartInstance.controller.getDatasetMeta(i);
                    meta.data.forEach(function (bar, index) {
                        let data = dataset.data[index];
                        ctx.fillText(data, bar._model.x - 8, bar._model.y - 5);
                    });
                });
            }
        },
        legend: {
            display: false
        },
        title: {
            display: true,
            fontColor: '#e2e2e2'
        },
        scales: {
            yAxes: [{
                ticks: {
                    fontColor: '#e2e2e2'
                },
                gridLines: {
                    display: false
                }
            }],
            xAxes: [{
                ticks: {
                    fontColor: '#e2e2e2'
                },
                gridLines: {
                    display: false
                },
            }]
        },
    }
};
new Chart(document.getElementById('lengths-movies').getContext('2d'), movies_lengths_config);



let movies_periods_labels = $('#periods-movies-bar').attr('values-y').split(', ');
let movies_periods_data = $('#periods-movies-bar').attr('values-x').split(', ');
movies_periods_labels.pop();
movies_periods_data.pop();

let movies_periods_config = {
    type: 'bar',
    data: {
        labels: movies_periods_labels,
        datasets: [{
            data: movies_periods_data,
            backgroundColor: [
                'rgba(255, 99, 132, 0.8)',
                'rgba(255, 159, 64, 0.8)',
                'rgba(255, 205, 86, 0.8)',
                'rgba(75, 192, 192, 0.8)',
                'rgba(54, 162, 235, 0.8)',
                'rgba(153, 102, 255, 0.8)',
                'rgba(201, 203, 207, 0.8)'
            ],
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

                this.data.datasets.forEach(function (dataset, i) {
                    let meta = chartInstance.controller.getDatasetMeta(i);
                    meta.data.forEach(function (bar, index) {
                        let data = dataset.data[index];
                        ctx.fillText(data, bar._model.x - 8, bar._model.y - 5);
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
                    fontColor: '#e2e2e2'
                },
                gridLines: {
                    display: false
                },
            }],
            xAxes: [{
                ticks: {
                    fontColor: '#e2e2e2'
                },
                gridLines: {
                    display: false
                },
            }]
        },
        title: {
            display: true,
            fontColor: '#e2e2e2'
        },
    }
};
new Chart(document.getElementById('periods-movies').getContext('2d'), movies_periods_config);



let movies_genres_labels = $('#genres-movies-bar').attr('values-y').split(', ');
let movies_genres_data = $('#genres-movies-bar').attr('values-x').split(', ');
movies_genres_labels.pop();
movies_genres_data.pop();

let movies_genres_config = {
    type: 'pie',
    data: {
        datasets: [{
            data: movies_genres_data,
            backgroundColor: [
                'rgba(255, 99, 132, 0.8)',
                'rgba(255, 159, 64, 0.8)',
                'rgba(255, 205, 86, 0.8)',
                'rgba(75, 192, 192, 0.8)',
                'rgba(54, 162, 235, 0.8)',
                'rgba(153, 102, 255, 0.8)',
                'rgba(201, 203, 207, 0.8)',
                'rgba(75, 99, 148, 0.8)',
                'rgb(73, 110, 54, 0.8)',
                'rgb(74, 32, 46, 0.8)'
            ],
            borderColor: '#212529',
            borderWidth: 1,
            label: 'by_media'
        }],
        labels: movies_genres_labels
    },
    options: {
        events: false,
        responsive: true,
        maintainAspectRatio: false,
        animation: {
            duration: 1,
            onComplete: function () {
                let ctx = this.chart.ctx;
                ctx.textAlign = 'center';
                ctx.textBaseline = 'bottom';

                this.data.datasets.forEach(function (dataset) {
                    for (let i = 0; i < dataset.data.length; i++) {
                        let model = dataset._meta[Object.keys(dataset._meta)[0]].data[i]._model,
                        total = dataset._meta[Object.keys(dataset._meta)[0]].total,
                        mid_radius = model.innerRadius + (model.outerRadius - model.innerRadius) / 2,
                        start_angle = model.startAngle,
                        end_angle = model.endAngle,
                        mid_angle = start_angle + (end_angle - start_angle) / 2;

                        let x = mid_radius * Math.cos(mid_angle);
                        let y = mid_radius * Math.sin(mid_angle);

                        if (Math.round(dataset.data[i] / total * 100) > 4) {
                            let percent = String(Math.round(dataset.data[i]));
                            ctx.font = "16px 'Helvetica Neue', Helvetica, Arial, sans-serif";
                            ctx.fillStyle = 'lightgrey';
                            ctx.fillText(percent, model.x + x, model.y + y + 10);
                        }
                    }
                });
            }
        },
        legend: {
            display: true,
            position: 'right',
            color: 'white',
        }
    }
};
new Chart(document.getElementById('genres-movies').getContext('2d'), movies_genres_config);



let movies_actors_labels = $('#actors-movies-bar').attr('values-y').split(', ');
let movies_actors_data = $('#actors-movies-bar').attr('values-x').split(', ');
movies_actors_labels.pop();
movies_actors_data.pop();

let movies_actors_config = {
    type: 'pie',
    data: {
        datasets: [{
            data: movies_actors_data,
            backgroundColor: [
                'rgba(255, 99, 132, 0.8)',
                'rgba(255, 159, 64, 0.8)',
                'rgba(255, 205, 86, 0.8)',
                'rgba(75, 192, 192, 0.8)',
                'rgba(54, 162, 235, 0.8)',
                'rgba(153, 102, 255, 0.8)',
                'rgba(201, 203, 207, 0.8)',
                'rgba(75, 99, 148, 0.8)',
                'rgb(73, 110, 54, 0.8)',
                'rgb(74, 32, 46, 0.8)'
            ],
            borderColor: '#212529',
            borderWidth: 1,
            label: 'by_media'
        }],
        labels: movies_actors_labels
    },
    options: {
        events: false,
        responsive: true,
        maintainAspectRatio: false,
        animation: {
            duration: 1,
            onComplete: function () {
                let ctx = this.chart.ctx;
                ctx.textAlign = 'center';
                ctx.textBaseline = 'bottom';

                this.data.datasets.forEach(function (dataset) {
                    for (let i = 0; i < dataset.data.length; i++) {
                        let model = dataset._meta[Object.keys(dataset._meta)[0]].data[i]._model,
                        total = dataset._meta[Object.keys(dataset._meta)[0]].total,
                        mid_radius = model.innerRadius + (model.outerRadius - model.innerRadius) / 2,
                        start_angle = model.startAngle,
                        end_angle = model.endAngle,
                        mid_angle = start_angle + (end_angle - start_angle) / 2;

                        let x = mid_radius * Math.cos(mid_angle);
                        let y = mid_radius * Math.sin(mid_angle);

                        let percent = String(Math.round(dataset.data[i]));
                        ctx.font = "16px 'Helvetica Neue', Helvetica, Arial, sans-serif";
                        ctx.fillStyle = 'lightgrey';
                        ctx.fillText(percent, model.x + x, model.y + y + 10);
                    }
                });
            }
        },
        legend: {
            display: true,
            position: 'right',
            color: 'white',
        }
    }
};
new Chart(document.getElementById('actors-movies').getContext('2d'), movies_actors_config);



let movies_directors_labels = $('#directors-movies-bar').attr('values-y').split(', ');
let movies_directors_data = $('#directors-movies-bar').attr('values-x').split(', ');
movies_directors_labels.pop();
movies_directors_data.pop();

let directors_actors_config = {
    type: 'pie',
    data: {
        datasets: [{
            data: movies_directors_data,
            backgroundColor: [
                'rgba(255, 99, 132, 0.8)',
                'rgba(255, 159, 64, 0.8)',
                'rgba(255, 205, 86, 0.8)',
                'rgba(75, 192, 192, 0.8)',
                'rgba(54, 162, 235, 0.8)',
                'rgba(153, 102, 255, 0.8)',
                'rgba(201, 203, 207, 0.8)',
                'rgba(75, 99, 148, 0.8)',
                'rgb(73, 110, 54, 0.8)',
                'rgb(74, 32, 46, 0.8)'
            ],
            borderColor: '#212529',
            borderWidth: 1,
            label: 'by_media'
        }],
        labels: movies_directors_labels
    },
    options: {
        events: false,
        responsive: true,
        maintainAspectRatio: false,
        animation: {
            duration: 1,
            onComplete: function () {
                let ctx = this.chart.ctx;
                ctx.textAlign = 'center';
                ctx.textBaseline = 'bottom';

                this.data.datasets.forEach(function (dataset) {
                    for (let i = 0; i < dataset.data.length; i++) {
                        let model = dataset._meta[Object.keys(dataset._meta)[0]].data[i]._model,
                        total = dataset._meta[Object.keys(dataset._meta)[0]].total,
                        mid_radius = model.innerRadius + (model.outerRadius - model.innerRadius) / 2,
                        start_angle = model.startAngle,
                        end_angle = model.endAngle,
                        mid_angle = start_angle + (end_angle - start_angle) / 2;

                        let x = mid_radius * Math.cos(mid_angle);
                        let y = mid_radius * Math.sin(mid_angle);

                        let percent = String(Math.round(dataset.data[i]));
                        ctx.font = "16px 'Helvetica Neue', Helvetica, Arial, sans-serif";
                        ctx.fillStyle = 'lightgrey';
                        ctx.fillText(percent, model.x + x, model.y + y + 10);
                    }
                });
            }
        },
        legend: {
            display: true,
            position: 'right',
            color: 'white',
        }
    }
};
new Chart(document.getElementById('directors-movies').getContext('2d'), directors_actors_config);



let movies_langage_labels = $('#langage-movies-bar').attr('values-y').split(', ');
let movies_langage_data = $('#langage-movies-bar').attr('values-x').split(', ');
movies_langage_labels.pop();
movies_langage_data.pop();

let movies_langage_config = {
    type: 'pie',
    data: {
        datasets: [{
            data: movies_langage_data,
            backgroundColor: [
                'rgba(255, 99, 132, 0.8)',
                'rgba(255, 159, 64, 0.8)',
                'rgba(255, 205, 86, 0.8)',
                'rgba(75, 192, 192, 0.8)',
                'rgba(54, 162, 235, 0.8)',
                'rgba(153, 102, 255, 0.8)',
                'rgba(201, 203, 207, 0.8)',
                'rgba(75, 99, 148, 0.8)',
                'rgb(73, 110, 54, 0.8)',
                'rgb(74, 32, 46, 0.8)'
            ],
            borderColor: '#212529',
            borderWidth: 1,
            label: 'by_media'
        }],
        labels: movies_langage_labels
    },
    options: {
        events: false,
        responsive: true,
        maintainAspectRatio: false,
        animation: {
            duration: 1,
            onComplete: function () {
                let ctx = this.chart.ctx;
                ctx.textAlign = 'center';
                ctx.textBaseline = 'bottom';

                this.data.datasets.forEach(function (dataset) {
                    for (let i = 0; i < dataset.data.length; i++) {
                        let model = dataset._meta[Object.keys(dataset._meta)[0]].data[i]._model,
                        // total = dataset._meta[Object.keys(dataset._meta)[0]].total,
                        mid_radius = model.innerRadius + (model.outerRadius - model.innerRadius) / 2,
                        start_angle = model.startAngle,
                        end_angle = model.endAngle,
                        mid_angle = start_angle + (end_angle - start_angle) / 2;

                        if ((Math.abs(end_angle) - Math.abs(start_angle)) > 0.2 ) {
                            let x = mid_radius * Math.cos(mid_angle);
                            let y = mid_radius * Math.sin(mid_angle);

                            let percent = String(Math.round(dataset.data[i]));
                            ctx.font = "16px 'Helvetica Neue', Helvetica, Arial, sans-serif";
                            ctx.fillStyle = 'lightgrey';
                            ctx.fillText(percent, model.x + x, model.y + y + 10);
                        }
                    }
                });
            }
        },
        legend: {
            display: true,
            position: 'right',
            color: 'white',
        }
    }
};
new Chart(document.getElementById('langage-movies').getContext('2d'), movies_langage_config);
