
function showmore() {
    $('.none-movies').attr("style", "display: block;");
    $('.more').attr("style", 'display: none;');
    $('.less').attr("style", 'display: block;');
    $(window).scrollTop(0)
}

function showless() {
    var i = 0;
    $('.movies').each(function () {
        i++;
        console.log(i);
        if (i > 6) {
            $(this).attr('style', 'display: none;');
            $(this).attr('class', 'col-xl-4 movies none-movies');
        } else {
            $(this).attr('style', 'display: block;');
        }
    });
    $('.more').attr("style", 'display: block;');
    $('.less').attr("style", 'display: none;');
    $(window).scrollTop(0)
}