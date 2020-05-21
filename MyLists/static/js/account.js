
// --- Follow status ----------------------------------------------
function follow_status(follow_id) {
    let status;

    if ($('.follow-btn')[0].innerText === 'UNFOLLOW') {
        $('.follow-btn').text('Follow');
        $('.follow-btn').addClass('btn-primary').removeClass('btn-dark');
        status = false;
    } else {
        $('.follow-btn').text('Unfollow');
        $('.follow-btn').removeClass('btn-primary').addClass('btn-dark');
        status = true;
    }

    $body = $("body");
    $.ajax ({
        type: "POST",
        url: "/follow_status",
        contentType: "application/json",
        data: JSON.stringify({follow_id: follow_id, follow_status: status}),
        dataType: "json",
        success: function(response) {
            console.log("ok");
        }
    });
}


// --- Canvas Data ------------------------------------------------
let time_data = $('#time-spent-pie').attr('values').split(', ');


// --- Time sent pie graph ----------------------------------------
let config = {
    type: 'pie',
    data: {
        datasets: [{
            data: time_data,
            backgroundColor: ['#216e7d', '#945141', '#8c7821'],
            borderColor: 'black',
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
                        if (i === 3){ // Darker text color for lighter background
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
                fontSize: 14,
            }
        },
    }
};
let ctx = document.getElementById('media-time').getContext('2d');
let myPie = new Chart(ctx, config);


// ------------------------------------------------------------------------
$(document).ready(function() {
    $body = $("body");
    $body.addClass("loading");
    $(document).click(function() {
        $body.removeClass("loading");
    });

    // Stats for the figure (series/anime/movies)
    $('.value').each(function() {
        var text = $(this).attr('id');
        $(this).parent().css('width', text);
    });

    // Tooltip initialization
    $(function () {
        $('[data-toggle="tooltip"]').tooltip()
    })

    // Levels animations for overview tab
    $(".xp-increase-fx-flicker").css("opacity", "1");
    $(".xp-increase-fx-flicker").animate({"opacity":Math.random()}, 100);
    $(".xp-increase-fx").css("display", "inline-block");

    $("#xp-bar-fill-series").css("box-shadow", "-5px 0px 10px #fff inset");
    setTimeout(function() {
        $("#xp-bar-fill-series").css("-webkit-transition", "all 2s ease");
        var series_percent = $("#xp-bar-fill-series").attr('data-percentage');
        $("#xp-bar-fill-series").css("width", series_percent+"%");
    }, 100);
    setTimeout(function(){
        $(".xp-increase-fx").fadeOut(500);
        $("#xp-bar-fill-series").css({"-webkit-transition":"all 0.5s ease","box-shadow":""});
    }, 2000);

    $("#xp-bar-fill-anime").css("box-shadow", "-5px 0px 10px #fff inset");
    setTimeout(function() {
        $("#xp-bar-fill-anime").css("-webkit-transition", "all 2s ease");
        var anime_percent = $("#xp-bar-fill-anime").attr('data-percentage');
        $("#xp-bar-fill-anime").css("width", anime_percent+"%");
    }, 100);
    setTimeout(function() {
        $(".xp-increase-fx").fadeOut(500);$("#xp-bar-fill-anime").css({"-webkit-transition":"all 0.5s ease","box-shadow":""});
    }, 2000);

    $("#xp-bar-fill-movies").css("box-shadow", "-5px 0px 10px #fff inset");
    setTimeout(function() {
        $("#xp-bar-fill-movies").css("-webkit-transition", "all 2s ease");
        var movies_percent = $("#xp-bar-fill-movies").attr('data-percentage');
        $("#xp-bar-fill-movies").css("width", movies_percent+"%");
    }, 100);
    setTimeout(function(){
        $(".xp-increase-fx").fadeOut(500);
        $("#xp-bar-fill-movies").css({"-webkit-transition":"all 0.5s ease","box-shadow":""});
    }, 2000);
});


