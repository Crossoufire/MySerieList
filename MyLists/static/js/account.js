
// ------------------------ Follow status ---------------------------------
function follow_status(follow_id) {
    var status;

    if ($('.follow-btn').text() == 'Unfollow') {
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