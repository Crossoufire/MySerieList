
function showmore(show, media) {
    var media = media;
    var show = show;

    $('#'+show).text("Show less...");
    $('#'+show).attr("onclick", "showless(\"" + show + "\", \"" + media + "\")");
    $('.'+media).attr("style", "display: block;");
}

function showless(show, media) {
    var i = 0;
    $('.'+media).each(function () {
        i++;
        if (i > 6) {
            $(this).attr('style', 'display: none;');
        } else {
            $(this).attr('style', 'display: block;');
        }
    });
    $('#'+show).text("Show more...");
    $('#'+show).attr("onclick", "showmore(\"" + show + "\", \"" + media + "\")");
}



