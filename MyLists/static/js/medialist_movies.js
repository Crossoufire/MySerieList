

// --- Create the cat buttons list ---------------------------
function chargeButtons(card, element_id, genres, media_list) {
    removeCat();

    if ($('#'+card.id).parent().hasClass('category-COMPLETED')) {
        var display_completed = "none;";
        var display_plan_to_watch = "block;";
    }
    else if ($('#'+card.id).parent().hasClass('category-ANIMATION')) {
        var display_completed = "none;";
        var display_plan_to_watch = "block;";
    }
    else {
        var display_completed = "block;";
        var display_plan_to_watch = "none;";
    }

    $(card).find('.view.overlay').prepend (
    "<ul class='card-cat-buttons'>" +
        "<li style='display: " + display_completed + "' class='btn btn-light p-1 m-1 card-btn-mobile' onclick='changeCategory(this,\"" + element_id + "\", \"" + card.id + "\",  \"" + genres + "\", \"" + media_list + "\")'>Completed</li>" +
        "<li style='display: " + display_plan_to_watch + "' class='btn btn-light p-1 m-1 card-btn-mobile' onclick='changeCategory(this, \"" + element_id + "\", \"" + card.id + "\", \"" + genres + "\",  \"" + media_list + "\")'>Plan to Watch</li>" +
    "</ul>");

    $(card).find('.card-btn-top-left').attr('style', 'display: none;');
    $(card).find('.card-btn-top-right').attr('style', 'display: none;');
    $(card).find('.mask').hide();
    $(card).find('.view.overlay').prepend("<a class='card-btn-top-right-2 fas fa-times' onclick='removeCat()')></a>");
    $(card).find('.card-img-top').attr('style', 'filter: brightness(20%); height: auto;');
}


// --- Change category ---------------------------------------
function changeCategory(new_category, element_id, card_id, genres, media_list) {
    var new_cat = new_category.childNodes[0].data
    removeCat();

    if ($('#'+card_id).parent().hasClass('category-COMPLETED')) {
        $("#"+card_id).prependTo(".category-PLAN.TO.WATCH");
        new_category = "Plan to Watch";
    }
    else if ($('#'+card_id).parent().hasClass('category-ANIMATION')) {
        $("#"+card_id).prependTo(".category-PLAN.TO.WATCH");
        new_category = "Plan to Watch";
    }
    else {
        if (genres.includes("Animation")) {
            $("#"+card_id).prependTo(".category-ANIMATION");
            new_category = "Completed Animation";
        } else {
            $("#"+card_id).prependTo(".category-COMPLETED");
            new_category = "Completed";
        }
    }

    $categories.isotope('layout');

    $body = $("body");
    $.ajax ({
        type: "POST",
        url: "/change_element_category",
        contentType: "application/json",
        data: JSON.stringify({status: new_category, element_id: element_id, element_type: media_list }),
        dataType: "json",
        success: function(response) {
            console.log("ok");
        }
    });
}



// --- FROM OTHER LISTS ---------------------------------------------------------------------

// --- Charge the buttons from other lists -------------------
function ChargeButtonsMovies(card_id, element_id, media_type) {
    removeCat();

    $('#'+card_id).children().children().first().prepend (
    "<ul class='card-cat-buttons'>" +
        "<li style='display: block;' class='btn btn-light p-1 m-1 card-btn-mobile' onclick='AddCatUser(this, \"" + card_id + "\", \"" + element_id + "\", \"" + media_type + "\")')'>Completed</li>" +
        "<li style='display: block;' class='btn btn-light p-1 m-1 card-btn-mobile' onclick='AddCatUser(this, \"" + card_id + "\", \"" + element_id + "\", \"" + media_type + "\")')'>Plan to Watch</li>" +
    "</ul>");

    $('#'+card_id).children().children().children('.card-btn-top-left').attr('style', 'display: none;');
    $('#'+card_id).children().children().children('.mask').hide();
    $('#'+card_id).children().children().first().prepend("<a class='card-btn-top-right-2 fas fa-times' onclick='removeCat()')></a>");
    $('#'+card_id).children().children().children('.card-img-top').attr('style', 'filter: brightness(20%); height: auto;');
}
