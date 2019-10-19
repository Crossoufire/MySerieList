
function follow(follow_id) {
    $('.follow_button').text('Unfollow');
    $('.follow_button').attr('onclick', 'unfollow('+follow_id+')');
    $('.follow_button').addClass('btn-dark');
    $('.follow_button').removeClass('btn-primary');

    $.ajax ({
        type: "POST",
        url: "/follow",
        contentType: "application/json",
        data: JSON.stringify({follow: follow_id}),
        dataType: "json",
        success: function(response) {
            console.log("ok"); }
    });
}


function unfollow(follow_id) {
    $('.follow_button').text('Follow');
    $('.follow_button').attr('onclick', 'follow('+follow_id+')');
    $('.follow_button').addClass('btn-primary');
    $('.follow_button').removeClass('btn-dark');

    $body = $("body");
    $.ajax ({
        type: "POST",
        url: "/unfollow",
        contentType: "application/json",
        data: JSON.stringify({unfollow: follow_id}),
        dataType: "json",
        success: function(response) {
            console.log("ok"); }
    });
}


function changeTab(tab, nav) {
    $('#'+tab);
    $('#overview').attr('class', 'nav-link');
    $('#'+nav).attr('class', 'nav-link active');
    $('#overview_tab').attr('class', 'tab-pane fade');
    $('#'+tab).attr('class', 'tab-pane fade show active');
}


function changeBadges(media) {
    if (media == 'anime') {
        $('#anime_badges').attr('style', 'display: block;');
        $('#series_badges').attr('style', 'display: none;');
        $('#movies_badges').attr('style', 'display: none;');
    } else if (media == 'series') {
        $('#anime_badges').attr('style', 'display: none;');
        $('#series_badges').attr('style', 'display: block;');
        $('#movies_badges').attr('style', 'display: none;');
    } else {
        $('#anime_badges').attr('style', 'display: none;');
        $('#series_badges').attr('style', 'display: none;');
        $('#movies_badges').attr('style', 'display: block;');
    }
}


$('.filters-button-group').each(function(i, buttonGroup) {
    var $buttonGroup = $(buttonGroup);
    $buttonGroup.on('click', 'button', function() {
        $buttonGroup.find('.btn-warning').addClass('btn-light');
        $buttonGroup.find('.btn-warning').removeClass('btn-warning');
        $(this).addClass('btn-warning');
        $(this).removeClass('btn-light');
    });
});


$(document).ready(function() {
    $body = $("body");
    $body.addClass("loading");
    $(document).click(function() {
        $body.removeClass("loading");
    });

    // Statistics and achievements % for the figure (anime/series/movies)
    $('.value').each(function() {
        var text = $(this).attr('id');
        $(this).parent().css('width', text);
    });

    // Tooltip initialization
    $('.block').tooltip();
    $('.block_no_data').tooltip();
    $(function () {
    $('[data-toggle="tooltip"]').tooltip()
    })
});