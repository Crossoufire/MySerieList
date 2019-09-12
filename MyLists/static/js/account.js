
function follow(follow_id) {
    // the follow button has to change to "unfollow";

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
    // the follow button has to change to "follow";

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


$(document).ready(function() {
    $body = $("body");
    $body.addClass("loading");
    $(document).click(function() {
        $body.removeClass("loading");
    });

    // Statistics size for the figure (anime/series/movies)
    $('.value').each(function() {
        var text = $(this).attr('id');
        $(this).parent().css('width', text);
    });

    // Tooltip initialization
    $('.block').tooltip();
    $(function () {
    $('[data-toggle="tooltip"]').tooltip()
    })

    // Tooltip initialization
    $('.block_no_data').tooltip();
    $(function () {
    $('[data-toggle="tooltip"]').tooltip()
    })
});