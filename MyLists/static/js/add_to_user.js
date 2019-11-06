

// -------------- Charge the buttons to choose the category -------------------
function add_user(card_id, element_id, media_type) {
    remove_cat();

    $('#'+card_id).children().first().prepend(
    "<ul class='cat_buttons'>" +
        "<li style='display: block;' class='btn btn_sm btn-light p-1 m-1 cat_buttons_pos' onclick='add_to_user(this, \"" + card_id + "\", \"" + element_id + "\", \"" + media_type + "\")'>Watching</li>" +
        "<li style='display: block;' class='btn btn_sm btn-light p-1 m-1 cat_buttons_pos' onclick='add_to_user(this, \"" + card_id + "\", \"" + element_id + "\", \"" + media_type + "\")')'>Completed</li>" +
        "<li style='display: block;' class='btn btn_sm btn-light p-1 m-1 cat_buttons_pos' onclick='add_to_user(this, \"" + card_id + "\", \"" + element_id + "\", \"" + media_type + "\")')'>On Hold</li>" +
        "<li style='display: block;' class='btn btn_sm btn-light p-1 m-1 cat_buttons_pos' onclick='add_to_user(this, \"" + card_id + "\", \"" + element_id + "\", \"" + media_type + "\")')'>Random</li>" +
        "<li style='display: block;' class='btn btn_sm btn-light p-1 m-1 cat_buttons_pos' onclick='add_to_user(this, \"" + card_id + "\", \"" + element_id + "\", \"" + media_type + "\")')'>Dropped</li>" +
        "<li style='display: block;' class='btn btn_sm btn-light p-1 m-1 cat_buttons_pos' onclick='add_to_user(this, \"" + card_id + "\", \"" + element_id + "\", \"" + media_type + "\")')'>Plan to Watch</li>" +
    "</ul>");

    $('#'+card_id).children().children('.btn_left').attr('style', 'display: none;');
    $('#'+card_id).children().children('.btn_bottom_left').attr('style', 'display: none;');
    $('#'+card_id).children().children('.mask').hide();
    $('#'+card_id).children().first().prepend("<a class='btn_right_2 fas fa-times' onclick='remove_cat()')></a>");
    $('#'+card_id).children().children('.card-img-top').attr('style', 'filter: brightness(0%);');
}

// -------------------- Add the category to the user --------------------------
function add_to_user(cat, card_id, element_id, media_type) {
    var add_cat = cat.childNodes[0].data

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
    remove_cat();
    $("#"+card_id).children().append("<div class='ribbon'></div>");
    $("#"+card_id).children().children().remove(".btn_left.fas.fa-plus.text-light");
}


// ---------- Charge the buttons to choose the category for movies ------------
function add_user_movies(card_id, element_id, media_type) {
    remove_cat();

    $('#'+card_id).children().first().prepend(
    "<ul class='cat_buttons'>" +
        "<li style='display: block;' class='btn btn_sm btn-light p-1 m-1 cat_buttons_pos' onclick='add_to_user(this, \"" + card_id + "\", \"" + element_id + "\", \"" + media_type + "\")')'>Completed</li>" +
        "<li style='display: block;' class='btn btn_sm btn-light p-1 m-1 cat_buttons_pos' onclick='add_to_user(this, \"" + card_id + "\", \"" + element_id + "\", \"" + media_type + "\")')'>Plan to Watch</li>" +
    "</ul>");

    $('#'+card_id).children().children('.btn_left').attr('style', 'display: none;');
    $('#'+card_id).children().children('.btn_bottom_left').attr('style', 'display: none;');
    $('#'+card_id).children().children('.mask').hide();
    $('#'+card_id).children().first().prepend("<a class='btn_right_2 fas fa-times' onclick='remove_cat()')></a>");
    $('#'+card_id).children().children('.card-img-top').attr('style', 'filter: brightness(0%);');
}

