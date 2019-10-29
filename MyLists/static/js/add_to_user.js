
function add_user(element_id, media_type, add_cat, card_id) {
    $body = $("body");
    $.ajax ({
        type: "POST",
        url: "/add_to_medialist",
        contentType: "application/json",
        data: JSON.stringify({ add_cat: add_cat, element_id: element_id, media_type: media_type }),
        dataType: "json",
        success: function(response) {
            console.log("ok");
        }
    });
    $("#"+card_id).children().append("<div class='ribbon'></div>");
    $("#"+card_id).children().children().remove(".btn_left.fas.fa-plus.text-light");
}