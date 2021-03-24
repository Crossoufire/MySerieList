

// --- Show more media: 6 to 12 ----------------------------------------------------------------------
function showmore(show, media) {
    let $show = $('#'+show);

    $show.text("Show less...");
    $show.attr("onclick", "showless(\"" + show + "\", \"" + media + "\")");
    $('.'+media).attr("style", "display: block;");
}


// --- Show less media: 12 to 6 ----------------------------------------------------------------------
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


// --- Change anime img size -------------------------------------------------------------------------
$(document).ready(function() {
    function resizeAnimeImg() {
        let $anime_img = $('.img-anime');
        let width = $anime_img.width();
        let height = width*1.5+'px';
        $anime_img.attr('style', 'height: '+ height);
    }
    $(window).resize(resizeAnimeImg).trigger('resize');
});
