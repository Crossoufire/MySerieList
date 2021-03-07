const series = $('.right-series');
const anime = $('.right-anime');
const movies = $('.right-movies');
const all = $('#all');
const series_active = $('#series');
const anime_active = $('#anime');
const movies_active = $('#movies');

let somme = series.length + anime.length + movies.length;

all.html('All &nbsp; (' + somme + ')');
series_active.html('Series &nbsp; (' + series.length + ')');
anime_active.html('Anime &nbsp; (' + anime.length + ')');
movies_active.html('Movies &nbsp; (' + movies.length + ')');

function show_results(media) {
    if (media === 'series') {
        series.show();
        anime.hide();
        movies.hide();

        if (series.length === 0) {
            remove_and_add('series')
        } else {
            $("#texti").remove();
        }

        all.removeClass('search-active').addClass('search-not-active');
        series_active.removeClass('search-not-active').addClass('search-active');
        anime_active.removeClass('search-active').addClass('search-not-active');
        movies_active.removeClass('search-active').addClass('search-not-active');
    }
    else if (media === 'anime') {
        series.hide();
        anime.show();
        movies.hide();

        if (anime.length === 0) {
            remove_and_add('anime')
        } else {
            $("#texti").remove();
        }

        all.removeClass('search-active').addClass('search-not-active');
        series_active.removeClass('search-active').addClass('search-not-active');
        anime_active.removeClass('search-not-active').addClass('search-active');
        movies_active.removeClass('search-active').addClass('search-not-active');
    }
    else if (media === 'movies') {
        series.hide();
        anime.hide();
        movies.show();

        if (movies.length === 0) {
            remove_and_add('movies')
        } else {
            $("#texti").remove();
        }

        all.removeClass('search-active').addClass('search-not-active');
        series_active.removeClass('search-active').addClass('search-not-active');
        anime_active.removeClass('search-active').addClass('search-not-active');
        movies_active.removeClass('search-not-active').addClass('search-active');
    }
    else {
        series.show();
        anime.show();
        movies.show();

        all.removeClass('search-not-active').addClass('search-active');
        series_active.removeClass('search-active').addClass('search-not-active');
        anime_active.removeClass('search-active').addClass('search-not-active');
        movies_active.removeClass('search-active').addClass('search-not-active');
    }
}

function remove_and_add(media) {
    $("#texti").remove();
    $(".add-text").append("<span id='texti'><i><b>No "+ media + " on this page.</b></i></span>");
}
