
// ---------------------------------- Global functions ----------------------------------------
//$(document).ready(function() {
//    // Tooltip initialization
//    $(function () {
//        $('[data-toggle="tooltip"]').tooltip()
//    })
//});

// -------------------- Add the media to the right list for the user --------------------------
function add_media(selected_cat, tmdb_id, media_type) {
    var hide_buttons = $('#buttons-'+tmdb_id);
    var change_title = $('#title-'+tmdb_id);
    var change_icon = $('#icon-'+tmdb_id)
    hide_buttons.html('Media successfully added to you list. ('+selected_cat+' category)');
    hide_buttons.attr('class', 'fs-18 p-t-10 text-center');
    change_title.text('Added to your list!');
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
