
// ---------------------------------- Global functions ----------------------------------------
//$(document).ready(function() {
//    // Tooltip initialization
//    $(function () {
//        $('[data-toggle="tooltip"]').tooltip()
//    })
//});

// -------------------- Add the media to the list for the user mobile version --------------------------
function add_media(selected_cat, tmdb_id, media_type) {
    let hide_buttons = $('#buttons-' + tmdb_id);
    let change_title = $('#title-'+tmdb_id);
    let change_title_container = $('#title-container-'+tmdb_id);
    let change_icon = $('#icon-'+tmdb_id)

    hide_buttons.hide();
    change_title.text('Added to your list');
    change_title.removeClass('disabled text-light');
    change_title_container.attr('class', 'fs-15 text-right m-r-10 m-b-5');
    change_icon.attr('class', 'fas fa-check');

    $body = $("body");
    $.ajax ({
        type: "POST",
        url: "/add_element",
        contentType: "application/json",
        data: JSON.stringify({ element_cat: selected_cat, element_id: tmdb_id,
        element_type: media_type, from_other_list: false }),
        dataType: "json",
        success: function(response) {
            console.log("ok");
        }
    });
}
