

// --- Show more media from 6 to 12 per media type -------------------------
function showmore(show, media) {
    let $show = $('#'+show);

    $show.text("Show less...");
    $show.attr("onclick", "showless(\"" + show + "\", \"" + media + "\")");
    $('.'+media).attr("style", "display: block;");
}


// --- Show less media from 12 to 6 per media type -------------------------
function showless(show, media) {
    let $show = $('#'+show);
    let i = 0;

    $('.'+media).each(function () {
        i++;
        if (i > 6) {
            $(this).attr('style', 'display: none;');
        } else {
            $(this).attr('style', 'display: block;');
        }
    });

    $show.text("Show more...");
    $show.attr("onclick", "showmore(\"" + show + "\", \"" + media + "\")");
}
