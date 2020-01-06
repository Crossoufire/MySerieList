
function showmore_movies() {
    $('.none-movies').attr("style", "display: block;");
    $('.more-movies').attr("style", 'display: none;');
    $('.less-movies').attr("style", 'display: block;');
    $(window).scrollTop(0)
}

function showless_movies() {
    var i = 0;
    $('.movies').each(function () {
        i++;
        if (i > 6) {
            $(this).attr('style', 'display: none;');
            $(this).attr('class', 'col-xl-4 movies none-movies');
        } else {
            $(this).attr('style', 'display: block;');
        }
    });
    $('.more-movies').attr("style", 'display: block;');
    $('.less-movies').attr("style", 'display: none;');
    $(window).scrollTop(0)
}

function showmore_series() {
    $('.none-series').attr("style", "display: block;");
    $('.more-series').attr("style", 'display: none;');
    $('.less-series').attr("style", 'display: block;');
    $(window).scrollTop(0)
}

function showless_series() {
    var i = 0;
    $('.series').each(function () {
        i++;
        console.log(i);
        if (i > 6) {
            $(this).attr('style', 'display: none;');
            $(this).attr('class', 'col-xl-4 series none-series');
        } else {
            $(this).attr('style', 'display: block;');
        }
    });
    $('.more-series').attr("style", 'display: block;');
    $('.less-series').attr("style", 'display: none;');
    $(window).scrollTop(0)
}