

// --- Follow status -------------------------------------------------------------------------------------
function follow_status(follow_id) {
    let status;
    let $follow_button = $('.follow-btn');

    status = $follow_button.prop('value') !== '1';
    $follow_button.addClass('disabled');
    $('.loading-follow').show();

    $.ajax ({
        type: "POST",
        url: "/follow_status",
        contentType: "application/json",
        data: JSON.stringify({follow_id: follow_id, follow_status: status}),
        dataType: "json",
        success: function() {
            if (status === false) {
                $follow_button.text('Follow');
                $follow_button.prop('value', '0');
                $follow_button.addClass('btn-primary').removeClass('btn-dark');
                $follow_button.removeClass('disabled');
            } else {
                $follow_button.text('Unfollow');
                $follow_button.prop('value', '1');
                $follow_button.removeClass('btn-primary').addClass('btn-dark');
                $follow_button.removeClass('disabled');
            }
        },
        error: function() {
            error_ajax_message('Error updating the following status. Please try again later.');
        },
        complete: function() {
            $('.loading-follow').hide();
        }
    });
}


// --- On document load -----------------------------------------------------------------------------------
$(document).ready(function() {
    // --- Time spent data -------------------------------------
    let time_data = $('#time-spent-pie').attr('values').split(', ');

    // --- Time spent pie graph --------------------------------
    let config_pie = {
        type: 'pie',
        data: {
            datasets: [{
                data: time_data,
                backgroundColor: ['#216e7d', '#945141', '#8c7821', '#196219'],
                borderColor: 'black',
                borderWidth: 1,
                label: 'by_media'
            }],
            labels: ['Series', 'Anime', 'Movies', 'Games']
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
                    ctx.textAlign = 'center';
                    ctx.textBaseline = 'bottom';

                    this.data.datasets.forEach(function (dataset) {
                        for (let i = 0; i < dataset.data.length; i++) {
                            let model = dataset._meta[Object.keys(dataset._meta)[0]].data[i]._model,
                            total = dataset._meta[Object.keys(dataset._meta)[0]].total,
                            mid_radius = model.innerRadius+(model.outerRadius-model.innerRadius)/2,
                            start_angle = model.startAngle,
                            end_angle = model.endAngle,
                            mid_angle = start_angle + (end_angle - start_angle)/2;

                            let x = mid_radius * Math.cos(mid_angle);
                            let y = mid_radius * Math.sin(mid_angle);

                            ctx.fillStyle = '#fff';
                            if (i === 4){ // Darker text color for lighter background
                                ctx.fillStyle = '#444';
                            }
                            let percent = String(Math.round(dataset.data[i]/total*100)) + "%";
                            //Don't Display If Legend is hide or value is 0
                            if(dataset.data[i] !== 0 && dataset._meta[0].data[i].hidden !== true) {
                                // ctx.fillText(dataset.data[i]+ " h", model.x + x, model.y + y);
                                // Display percent in another line, line break doesn't work for fillText
                                ctx.fillText(percent, model.x + x + 5, model.y + y + 10);
                            }
                        }
                    });
                }
            },
            legend: {
                position: 'bottom',
                labels: {
                    fontColor: '#e2e2e2',
                    fontSize: 12,
                }
            },
        }
    };
    let ctx = document.getElementById('media-time').getContext('2d');
    new Chart(ctx, config_pie);

    // --- Stats for the figure (series/anime/movies) ----------
    $('.value').each(function() {
        let text = $(this).attr('id');
        $(this).parent().css('width', text);
    });
});
