

// --- On document load ----------------------------------------------------------------------------------------
$(document).ready(function() {
    let time_data = $('#time-spent-pie').attr('values').split(', ');

    let config_pie = {
        type: 'pie',
        data: {
            datasets: [{
                data: time_data,
                backgroundColor: ['#216e7d', '#945141', '#8c7821'],
                borderColor: '#212529',
                borderWidth: 1,
                label: 'by_media'
            }],
            labels: ['Series', 'Anime', 'Movies']
        },
        options: {
            events: false,
            responsive: true,
            maintainAspectRatio: false,
            animation: {
                duration: 500,
                easing: "easeOutQuart",
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

                            let percent = String(Math.round(dataset.data[i] / total * 100)) + "%";

                            ctx.font = "16px 'Helvetica Neue', Helvetica, Arial, sans-serif";
                            ctx.fillStyle = 'lightgrey';
                            ctx.fillText(percent, model.x + x, model.y + y + 10);
                        }
                    });
                }
            },
            legend: {
                display: false,
            }
        }
    };
    let ctx = document.getElementById('media-time').getContext('2d');
    new Chart(ctx, config_pie);

    $('.value').each(function() {
        let text = $(this).attr('id');
        $(this).parent().css('width', text);
    });
});
