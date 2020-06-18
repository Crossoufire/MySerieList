

// --- Create the buttons category list --------------------
function chargeButtons(card, element_id, seas_drop_id, ep_drop_id, seas_data, media_list) {
    let display_watching, display_completed, display_on_hold, display_random, display_dropped, display_plan_to_watch;

    display_watching = "block;";
    display_completed = "block;";
    display_on_hold = "block;";
    display_random = "block;";
    display_dropped = "block;";
    display_plan_to_watch = "block;";

    removeCat();

    if ($('#'+card.id).parent().hasClass('category-WATCHING')) {
        display_watching = "none;";
    }
    else if ($('#'+card.id).parent().hasClass('category-COMPLETED')) {
        display_completed = "none;";
    }
    else if ($('#'+card.id).parent().hasClass('category-ON.HOLD')) {
        display_on_hold = "none;";
    }
    else if ($('#'+card.id).parent().hasClass('category-RANDOM')) {
        display_random = "none;";
    }
    else if ($('#'+card.id).parent().hasClass('category-DROPPED')) {
        display_dropped = "none;";
    }
    else {
        display_plan_to_watch = "none;";
    }

    $(card).find('.view.overlay').prepend (
    "<ul class='card-cat-buttons'>" +
        "<li style='display: " + display_watching + "' class='btn btn-light p-1 m-1 card-btn-mobile' onclick='changeCategory(this, \"" + element_id + "\", \"" + card.id + "\", \"" + seas_drop_id + "\", \"" + ep_drop_id + "\", \"" + seas_data + "\", \"" + media_list + "\")'>Watching</li>" +
        "<li style='display: " + display_completed + "' class='btn btn-light p-1 m-1 card-btn-mobile' onclick='changeCategory(this, \"" + element_id + "\", \"" + card.id + "\", \"" + seas_drop_id + "\", \"" + ep_drop_id + "\", \"" + seas_data + "\", \"" + media_list + "\")'>Completed</li>" +
        "<li style='display: " + display_on_hold + "' class='btn btn-light p-1 m-1 card-btn-mobile' onclick='changeCategory(this, \"" + element_id + "\", \"" + card.id + "\", \"" + seas_drop_id + "\", \"" + ep_drop_id + "\", \"" + seas_data + "\", \"" + media_list + "\")'>On Hold</li>" +
        "<li style='display: " + display_random + "' class='btn btn-light p-1 m-1 card-btn-mobile' onclick='changeCategory(this, \"" + element_id + "\", \"" + card.id + "\", \"" + seas_drop_id + "\", \"" + ep_drop_id + "\", \"" + seas_data + "\", \"" + media_list + "\")'>Random</li>" +
        "<li style='display: " + display_dropped + "' class='btn btn-light p-1 m-1 card-btn-mobile' onclick='changeCategory(this, \"" + element_id + "\", \"" + card.id + "\", \"" + seas_drop_id + "\", \"" + ep_drop_id + "\", \"" + seas_data + "\", \"" + media_list + "\")'>Dropped</li>" +
        "<li style='display: " + display_plan_to_watch + "' class='btn btn-light p-1 m-1 card-btn-mobile' onclick='changeCategory(this, \"" + element_id + "\", \"" + card.id + "\", \"" + seas_drop_id + "\", \"" + ep_drop_id + "\", \"" + seas_data + "\", \"" + media_list + "\")'>Plan to Watch</li>" +
    "</ul>");

    $(card).find('.card-btn-top-left').attr('style', 'display: none;');
    $(card).find('.card-btn-top-right').attr('style', 'display: none;');
    $(card).find('.seas-eps-box').attr('style', 'display: none;');
    $(card).find('.mask').hide();
    $(card).find('.view.overlay').prepend("<a class='card-btn-top-right-2 fas fa-times' onclick='removeCat()')></a>");
    $(card).find('.card-img-top').attr('style', 'filter: brightness(20%); height: auto;');
}


// --- Change the category ---------------------------------
function changeCategory(new_category, element_id, card_id, seas_drop_id, ep_drop_id, seas_data, media_list) {
    var new_cat = new_category.childNodes[0].data

    if (new_cat == 'Watching') {
        $("#"+card_id).prependTo(".category-WATCHING");
    }
    else if (new_cat == 'Completed') {
        $("#"+card_id).prependTo(".category-COMPLETED");

        var season_data = JSON.parse("[" + seas_data + "]");
        var episode_drop = document.getElementById(ep_drop_id);

        var seasons_length = $('#'+seas_drop_id).children('option').length;
        var seasons_index = (seasons_length - 1);
        $('#'+seas_drop_id).prop('selectedIndex', seasons_index);

        episode_drop.length = 1;

        for (i = 2; i <= season_data[0][seasons_index]; i++) {
            let opt = document.createElement("option");
            opt.className = "card-opt-box";
            if (i <= 9) {
                opt.text = "E0"+i;
            } else {
                opt.text = "E"+i;
            }
            episode_drop.appendChild(opt);
        }
        $('#'+ep_drop_id).prop('selectedIndex', season_data[0][seasons_index]-1);
    }
    else if (new_cat == 'On Hold') {
        $("#"+card_id).prependTo(".category-ON.HOLD");
    }
    else if (new_cat == 'Random') {
        $("#"+card_id).prependTo(".category-RANDOM");
    }
    else if (new_cat == 'Dropped') {
        $("#"+card_id).prependTo(".category-DROPPED");
    }
    else {
        $("#"+card_id).prependTo(".category-PLAN.TO.WATCH");
    }

    removeCat();
    $categories.isotope('layout');

    $.ajax ({
        type: "POST",
        url: "/change_element_category",
        contentType: "application/json",
        data: JSON.stringify({status: new_cat, element_id: element_id, element_type: media_list }),
        dataType: "json",
        success: function(response) {
            console.log("ok");
        },
        error: function () {
            error_ajax_message('Error changing the category of the media. PLease try again later.')
        }
    });
}


// --- Update episode --------------------------------------
function updateEpisode(element_id, episode, media_list) {
    var selected_episode = episode.selectedIndex

    $body = $("body");
    $categories.isotope('layout');
    $.ajax ({
        type: "POST",
        url: "/update_element_episode",
        contentType: "application/json",
        data: JSON.stringify({episode: selected_episode, element_id: element_id, element_type: media_list }),
        dataType: "json",
        success: function() {
            console.log("ok");
        },
        error: function () {
            error_ajax_message('Error updating the episode of the media. Please try again later.')
        }
    });
}


// --- Update season ---------------------------------------
function updateSeason(element_id, value, seas_data, ep_drop_id, media_list) {
    var selected_season = value.selectedIndex;
    var episode_drop = document.getElementById(ep_drop_id);
    var season_data = JSON.parse("[" + seas_data + "]");

    episode_drop.length = 1;
    for (i = 2; i <= season_data[0][selected_season]; i++) {
        let opt = document.createElement("option");
        opt.className = "card-opt-box";
        if (i <= 9) {
                opt.text = "E0"+i;
            } else {
                opt.text = "E"+i;
            }
        episode_drop.appendChild(opt);
    }

    $body = $("body");
    $categories.isotope('layout');
    $.ajax ({
        type: "POST",
        url: "/update_element_season",
        contentType: "application/json",
        data: JSON.stringify({season: selected_season, element_id: element_id, element_type: media_list }),
        dataType: "json",
        success: function(response) {
            console.log("ok");
        },
        error: function () {
            error_ajax_message('Error updating the season of the media. Please try again later.')
        }
    });
}


// --- FROM OTHER LISTS ----------------------------------------------------
// --- Charge the buttons to choose the category for tv --------------------
function ChargeButtonsTV(card_id, element_id, media_type) {
    removeCat();

    $('#'+card_id).children().children().first().prepend (
    "<ul class='card-cat-buttons'>" +
        "<li style='display: block;' class='btn btn-light p-1 m-1 card-btn-mobile' onclick='AddCatUser(this, \"" + card_id + "\", \"" + element_id + "\", \"" + media_type + "\")'>Watching</li>" +
        "<li style='display: block;' class='btn btn-light p-1 m-1 card-btn-mobile' onclick='AddCatUser(this, \"" + card_id + "\", \"" + element_id + "\", \"" + media_type + "\")')'>Completed</li>" +
        "<li style='display: block;' class='btn btn-light p-1 m-1 card-btn-mobile' onclick='AddCatUser(this, \"" + card_id + "\", \"" + element_id + "\", \"" + media_type + "\")')'>On Hold</li>" +
        "<li style='display: block;' class='btn btn-light p-1 m-1 card-btn-mobile' onclick='AddCatUser(this, \"" + card_id + "\", \"" + element_id + "\", \"" + media_type + "\")')'>Random</li>" +
        "<li style='display: block;' class='btn btn-light p-1 m-1 card-btn-mobile' onclick='AddCatUser(this, \"" + card_id + "\", \"" + element_id + "\", \"" + media_type + "\")')'>Dropped</li>" +
        "<li style='display: block;' class='btn btn-light p-1 m-1 card-btn-mobile' onclick='AddCatUser(this, \"" + card_id + "\", \"" + element_id + "\", \"" + media_type + "\")')'>Plan to Watch</li>" +
    "</ul>");

    $('#'+card_id).children().children().children('.card-btn-top-left').attr('style', 'display: none;');
    $('#'+card_id).children().children('.seas-eps-box').attr('style', 'display: none;');
    $('#'+card_id).children().children().children('.mask').hide();
    $('#'+card_id).children().children().first().prepend("<a class='card-btn-top-right-2 fas fa-times' onclick='removeCat()')></a>");
    $('#'+card_id).children().children().children('.card-img-top').attr('style', 'filter: brightness(20%); height: auto;');
}
