

// ------------- Update episode ---------------
function updateEpisode(element_id, episode, media_list) {
    var selected_episode = episode.selectedIndex

    $body = $("body");
    $.ajax ({
        type: "POST",
        url: "/update_element_episode",
        contentType: "application/json",
        data: JSON.stringify({episode: selected_episode, element_id: element_id, element_type: media_list }),
        dataType: "json",
        success: function(response) {
            console.log("ok"); }
    });
}


// -------------- Update season ---------------
function updateSeason(element_id, value, seas_data, ep_drop_id, media_list) {
    var selected_season = value.selectedIndex;
    var episode_drop = document.getElementById(ep_drop_id);
    var season_data = JSON.parse("[" + seas_data + "]");
    console.log(season_data);

    episode_drop.length = 1;

    for (i = 2; i <= season_data[0][selected_season]; i++) {
        let opt = document.createElement("option");
        opt.text = "E" + i;
        episode_drop.appendChild(opt);
    }

    $body = $("body");
    $.ajax ({
        type: "POST",
        url: "/update_element_season",
        contentType: "application/json",
        data: JSON.stringify({season: selected_season, element_id: element_id, element_type: media_list }),
        dataType: "json",
        success: function(response) {
            console.log("ok"); }
    });
}


// ------------------------- Anime/Series metadata --------------------------
function show_metadata(data, media_list) {
    $('#original_name').text('');
    $('#modal_title').html(data.name);
    if (data.name != data.original_name) {
        $('#original_name').html("<b>Original Name</b>: " +data.original_name);
    }
    $('#actors').html("<b>Actors</b>: " +data.actors);
    $('#genres').html("<b>Genres</b>: " +data.genres);
    $('#first_air_date').html("<b>First Air Date</b>: " +data.first_air_date);
    $('#last_air_date').html("<b>Last Air Date</b>: " +data.last_air_date);
    $('#networks').html("<b>Networks</b>: " +data.networks);
    $('#created_by').html("<b>Created By</b>: " +data.created_by);
    $('#episode_duration').html("<b>Episode Duration</b>: " +data.episode_duration+ " min");
    $('#total_seasons').html("<b>Total Seasons</b>: " +data.total_seasons);
    $('#total_episodes').html("<b>Total Episodes</b>: " +data.total_episodes);
    $('#episodes_per_season').html("<b>Episodes Per Season</b>: " +data.eps_per_season);
    if (media_list == "serieslist") {
        $('#origin_country').html("<b>Origin Country</b>: " +data.origin_country);
    }
    $('#tmdb_score').html("<b>TMDb Score</b>: " +data.vote_average+ "/10 &nbsp;(" +data.vote_count.toLocaleString("en")+ " votes)");
    $('#status').html("<b>Status</b>: " +data.status);
    $('#synopsis').html("<b>Synopsis</b>: " +data.synopsis);
}


// ------------------- Create the category list ---------------------
function charge_cat(card_id, element_id, seas_drop_id, ep_drop_id, seas_data, media_list) {
    remove_cat();

    if ($('#'+card_id).parent().hasClass('WATCHING')) {
        var display_watching = "none;";
        var display_completed = "block;";
        var display_on_hold = "block;";
        var display_random = "block;";
        var display_dropped = "block;";
        var display_plan_to_watch = "block;";
    }
    else if ($('#'+card_id).parent().hasClass('COMPLETED')) {
        var display_watching = "block;";
        var display_completed = "none;";
        var display_on_hold = "block;";
        var display_random = "block;";
        var display_dropped = "block;";
        var display_plan_to_watch = "block;";
    }
    else if ($('#'+card_id).parent().hasClass('ON.HOLD')) {
        var display_watching = "block;";
        var display_completed = "block;";
        var display_on_hold = "none;";
        var display_random = "block;";
        var display_dropped = "block;";
        var display_plan_to_watch = "block;";
    }
    else if ($('#'+card_id).parent().hasClass('RANDOM')) {
        var display_watching = "block;";
        var display_completed = "block;";
        var display_on_hold = "block;";
        var display_random = "none;";
        var display_dropped = "block;";
        var display_plan_to_watch = "block;";
    }
    else if ($('#'+card_id).parent().hasClass('DROPPED')) {
        var display_watching = "block;";
        var display_completed = "block;";
        var display_on_hold = "block;";
        var display_random = "block;";
        var display_dropped = "none;";
        var display_plan_to_watch = "block;";
    }
    else {
        var display_watching = "block;";
        var display_completed = "block;";
        var display_on_hold = "block;";
        var display_random = "block;";
        var display_dropped = "block;";
        var display_plan_to_watch = "none;";
    }

    $('#'+card_id).children().first().prepend(
    "<ul class='cat_buttons'>" +
        "<li style='display: " + display_watching + "' class='btn btn_sm btn-light p-1 m-1 cat_buttons_pos' onclick='changeCategory(this, \"" + element_id + "\", \"" + card_id + "\", \"" + seas_drop_id + "\", \"" + ep_drop_id + "\", \"" + seas_data + "\", \"" + media_list + "\")'>Watching</li>" +
        "<li style='display: " + display_completed + "' class='btn btn_sm btn-light p-1 m-1 cat_buttons_pos' onclick='changeCategory(this, \"" + element_id + "\", \"" + card_id + "\", \"" + seas_drop_id + "\", \"" + ep_drop_id + "\", \"" + seas_data + "\", \"" + media_list + "\")'>Completed</li>" +
        "<li style='display: " + display_on_hold + "' class='btn btn_sm btn-light p-1 m-1 cat_buttons_pos' onclick='changeCategory(this, \"" + element_id + "\", \"" + card_id + "\", \"" + seas_drop_id + "\", \"" + ep_drop_id + "\", \"" + seas_data + "\", \"" + media_list + "\")'>On Hold</li>" +
        "<li style='display: " + display_random + "' class='btn btn_sm btn-light p-1 m-1 cat_buttons_pos' onclick='changeCategory(this, \"" + element_id + "\", \"" + card_id + "\", \"" + seas_drop_id + "\", \"" + ep_drop_id + "\", \"" + seas_data + "\", \"" + media_list + "\")'>Random</li>" +
        "<li style='display: " + display_dropped + "' class='btn btn_sm btn-light p-1 m-1 cat_buttons_pos' onclick='changeCategory(this, \"" + element_id + "\", \"" + card_id + "\", \"" + seas_drop_id + "\", \"" + ep_drop_id + "\", \"" + seas_data + "\", \"" + media_list + "\")'>Dropped</li>" +
        "<li style='display: " + display_plan_to_watch + "' class='btn btn_sm btn-light p-1 m-1 cat_buttons_pos' onclick='changeCategory(this, \"" + element_id + "\", \"" + card_id + "\", \"" + seas_drop_id + "\", \"" + ep_drop_id + "\", \"" + seas_data + "\", \"" + media_list + "\")'>Plan to Watch</li>" +
    "</ul>");

    $('#'+card_id).children().children('.btn_left').attr('style', 'display: none;');
    $('#'+card_id).children().children('.btn_right').attr('style', 'display: none;');
    $('#'+card_id).children().children('.btn_bottom_left').attr('style', 'display: none;');
    $('#'+card_id).children().children('.mask').hide();
    $('#'+card_id).children().first().prepend("<a class='btn_right_2 fas fa-times' onclick='remove_cat()')></a>");
    $('#'+card_id).children().children('.card-img-top').attr('style', 'filter: brightness(0%);');
}


// ------------------------- Change category ------------------------
function changeCategory(new_category, element_id, card_id, seas_drop_id, ep_drop_id, seas_data, media_list) {
    var new_cat = new_category.childNodes[0].data

    if (new_cat == 'Watching') {
        $("#" + card_id).prependTo(".d-flex.flex-wrap.WATCHING");
        $("#" + card_id).children('.card-body').show();
        $("#" + card_id).children().children('.btn_bottom_left').show();
    }
    else if (new_cat == 'Completed') {
        $("#" + card_id).prependTo(".d-flex.flex-wrap.COMPLETED");
        $("#" + card_id).children('.card-body').show();
        $("#" + card_id).children().children('.btn_bottom_left').show();

        var season_data = JSON.parse("[" + seas_data + "]");
        var episode_drop = document.getElementById(ep_drop_id);

        var seasons_length = $('#'+seas_drop_id).children('option').length;
        var seasons_index = (seasons_length - 1);
        $('#'+seas_drop_id).prop('selectedIndex', seasons_index);

        episode_drop.length = 1;

        for (i = 2; i <= season_data[0][seasons_index]; i++) {
            let opt = document.createElement("option");
            opt.text = "Episode " + i;
            episode_drop.appendChild(opt);
        }
        $('#'+ep_drop_id).prop('selectedIndex', season_data[0][seasons_index]-1);
    }
    else if (new_cat == 'On Hold') {
        $("#" + card_id).prependTo(".d-flex.flex-wrap.ON.HOLD");
        $("#" + card_id).children('.card-body').show();
        $("#" + card_id).children().children('.btn_bottom_left').show();
    }
    else if (new_cat == 'Random') {
        $("#" + card_id).prependTo(".d-flex.flex-wrap.RANDOM");
        $("#" + card_id).children('.card-body').show();
        $("#" + card_id).children().children('.btn_bottom_left').show();
    }
    else if (new_cat == 'Dropped') {
        $("#" + card_id).prependTo(".d-flex.flex-wrap.DROPPED");
        $("#" + card_id).children('.card-body').show();
        $("#" + card_id).children().children('.btn_bottom_left').show();
    }
    else {
        $("#" + card_id).prependTo(".d-flex.flex-wrap.PLAN.TO.WATCH");
        $("#" + card_id).children('.card-body').hide();
        $("#" + card_id).children().children('.btn_bottom_left').hide();
    }

    $body = $("body");
    remove_cat();
    $categories.isotope('layout');
    $.ajax ({
        type: "POST",
        url: "/change_element_category",
        contentType: "application/json",
        data: JSON.stringify({status: new_cat, element_id: element_id, element_type: media_list }),
        dataType: "json",
        success: function(response) {
            console.log("ok");
        }
    });
}
