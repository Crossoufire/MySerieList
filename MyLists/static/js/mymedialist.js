
// ----------- Change category --------------
function changeCategory(element_id, new_category, card_id, mod_id, seas_drop_id, ep_drop_id, seas_data, media_list) {
    if (new_category === 'Watching') {
        var completed = 'Completed';
        var on_hold = 'On Hold';
        var random = 'Random';
        var dropped = 'Dropped';
        var plan_to_watch = 'Plan to Watch';

        $("#"+mod_id+ " a").filter(":contains('Watching')").remove()
        $("#"+mod_id+ " a").filter(":contains('Completed')").remove()
        $("#"+mod_id+ " a").filter(":contains('On Hold')").remove()
        $("#"+mod_id+ " a").filter(":contains('Random')").remove()
        $("#"+mod_id+ " a").filter(":contains('Dropped')").remove()
        $("#"+mod_id+ " a").filter(":contains('Plan to Watch')").remove()

        $("#"+mod_id).prepend(
            "<a data-dismiss='modal' class='list-group-item text-light bg-dark modded' onclick='changeCategory(\"" + element_id + "\", \"" + completed + "\", \"" + card_id + "\", \"" + mod_id + "\", \"" + seas_drop_id + "\", \"" + ep_drop_id + "\", \"" + seas_data + "\", \"" + media_list + "\")'>Completed</a>" +
            "<a data-dismiss='modal' class='list-group-item text-light bg-dark modded' onclick='changeCategory(\"" + element_id + "\", \"" + on_hold + "\", \"" + card_id + "\", \"" + mod_id + "\", \"" + seas_drop_id + "\", \"" + ep_drop_id + "\", \"" + seas_data + "\", \"" + media_list + "\")'>On Hold</a>" +
            "<a data-dismiss='modal' class='list-group-item text-light bg-dark modded' onclick='changeCategory(\"" + element_id + "\", \"" + random + "\", \"" + card_id + "\", \"" + mod_id + "\", \"" + seas_drop_id + "\", \"" + ep_drop_id + "\", \"" + seas_data + "\", \"" + media_list + "\")'>Random</a>" +
            "<a data-dismiss='modal' class='list-group-item text-light bg-dark modded' onclick='changeCategory(\"" + element_id + "\", \"" + dropped + "\", \"" + card_id + "\", \"" + mod_id + "\", \"" + seas_drop_id + "\", \"" + ep_drop_id + "\", \"" + seas_data + "\", \"" + media_list + "\")'>Dropped</a>" +
            "<a data-dismiss='modal' class='list-group-item text-light bg-dark modded' onclick='changeCategory(\"" + element_id + "\", \"" + plan_to_watch + "\", \"" + card_id + "\", \"" + mod_id + "\", \"" + seas_drop_id + "\", \"" + ep_drop_id + "\", \"" + seas_data + "\", \"" + media_list + "\")'>Plan to Watch</a>"
        );
        $("#" + card_id).prependTo(".d-flex.flex-wrap.WATCHING");
        $("#" + card_id).children('.card-body').show();
        $("#" + card_id).children().children('.btn_bottom_left').show();
        $('.modal').modal("hide");
    }

    if (new_category === 'Completed') {
        var watching = 'Watching';
        var on_hold = 'On Hold';
        var random = 'Random';
        var dropped = 'Dropped';
        var plan_to_watch = 'Plan to Watch';

        $("#"+mod_id+ " a").filter(":contains('Watching')").remove()
        $("#"+mod_id+ " a").filter(":contains('Completed')").remove()
        $("#"+mod_id+ " a").filter(":contains('On Hold')").remove()
        $("#"+mod_id+ " a").filter(":contains('Random')").remove()
        $("#"+mod_id+ " a").filter(":contains('Dropped')").remove()
        $("#"+mod_id+ " a").filter(":contains('Plan to Watch')").remove()

        $("#"+mod_id).prepend(
            "<a data-dismiss='modal' class='list-group-item text-light bg-dark modded' onclick='changeCategory(\"" + element_id + "\", \"" + watching + "\", \"" + card_id + "\", \"" + mod_id + "\", \"" + seas_drop_id + "\", \"" + ep_drop_id + "\", \"" + seas_data + "\", \"" + media_list + "\")'>Watching</a>" +
            "<a data-dismiss='modal' class='list-group-item text-light bg-dark modded' onclick='changeCategory(\"" + element_id + "\", \"" + on_hold + "\", \"" + card_id + "\", \"" + mod_id + "\", \"" + seas_drop_id + "\", \"" + ep_drop_id + "\", \"" + seas_data + "\", \"" + media_list + "\")'>On Hold</a>" +
            "<a data-dismiss='modal' class='list-group-item text-light bg-dark modded' onclick='changeCategory(\"" + element_id + "\", \"" + random + "\", \"" + card_id + "\", \"" + mod_id + "\", \"" + seas_drop_id + "\", \"" + ep_drop_id + "\", \"" + seas_data + "\", \"" + media_list + "\")'>Random</a>" +
            "<a data-dismiss='modal' class='list-group-item text-light bg-dark modded' onclick='changeCategory(\"" + element_id + "\", \"" + dropped + "\", \"" + card_id + "\", \"" + mod_id + "\", \"" + seas_drop_id + "\", \"" + ep_drop_id + "\", \"" + seas_data + "\", \"" + media_list + "\")'>Dropped</a>" +
            "<a data-dismiss='modal' class='list-group-item text-light bg-dark modded' onclick='changeCategory(\"" + element_id + "\", \"" + plan_to_watch + "\", \"" + card_id + "\", \"" + mod_id + "\", \"" + seas_drop_id + "\", \"" + ep_drop_id + "\", \"" + seas_data + "\", \"" + media_list + "\")'>Plan to Watch</a>"
        );
        $("#" + card_id).prependTo(".d-flex.flex-wrap.COMPLETED");
        $("#" + card_id).children('.card-body').show();
        $("#" + card_id).children().children('.btn_bottom_left').show();
        $('.modal').modal("hide");

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

    if (new_category === 'On Hold') {
        var completed = 'Completed';
        var watching = 'Watching';
        var random = 'Random';
        var dropped = 'Dropped';
        var plan_to_watch = 'Plan to Watch';

        $("#"+mod_id+ " a").filter(":contains('Watching')").remove()
        $("#"+mod_id+ " a").filter(":contains('Completed')").remove()
        $("#"+mod_id+ " a").filter(":contains('On Hold')").remove()
        $("#"+mod_id+ " a").filter(":contains('Random')").remove()
        $("#"+mod_id+ " a").filter(":contains('Dropped')").remove()
        $("#"+mod_id+ " a").filter(":contains('Plan to Watch')").remove()

        $("#"+mod_id).prepend(
            "<a data-dismiss='modal' class='list-group-item text-light bg-dark modded' onclick='changeCategory(\"" + element_id + "\", \"" + watching + "\", \"" + card_id + "\", \"" + mod_id + "\", \"" + seas_drop_id + "\", \"" + ep_drop_id + "\", \"" + seas_data + "\", \"" + media_list + "\")'>Watching</a>" +
            "<a data-dismiss='modal' class='list-group-item text-light bg-dark modded' onclick='changeCategory(\"" + element_id + "\", \"" + completed + "\", \"" + card_id + "\", \"" + mod_id + "\", \"" + seas_drop_id + "\", \"" + ep_drop_id + "\", \"" + seas_data + "\", \"" + media_list + "\")'>Completed</a>" +
            "<a data-dismiss='modal' class='list-group-item text-light bg-dark modded' onclick='changeCategory(\"" + element_id + "\", \"" + random + "\", \"" + card_id + "\", \"" + mod_id + "\", \"" + seas_drop_id + "\", \"" + ep_drop_id + "\", \"" + seas_data + "\", \"" + media_list + "\")'>Random</a>" +
            "<a data-dismiss='modal' class='list-group-item text-light bg-dark modded' onclick='changeCategory(\"" + element_id + "\", \"" + dropped + "\", \"" + card_id + "\", \"" + mod_id + "\", \"" + seas_drop_id + "\", \"" + ep_drop_id + "\", \"" + seas_data + "\", \"" + media_list + "\")'>Dropped</a>" +
            "<a data-dismiss='modal' class='list-group-item text-light bg-dark modded' onclick='changeCategory(\"" + element_id + "\", \"" + plan_to_watch + "\", \"" + card_id + "\", \"" + mod_id + "\", \"" + seas_drop_id + "\", \"" + ep_drop_id + "\", \"" + seas_data + "\", \"" + media_list + "\")'>Plan to Watch</a>"
        );
        $("#" + card_id).prependTo(".d-flex.flex-wrap.ON.HOLD");
        $("#" + card_id).children('.card-body').show();
        $("#" + card_id).children().children('.btn_bottom_left').show();
        $('.modal').modal("hide");
    }

    if (new_category === 'Random') {
        var completed = 'Completed';
        var on_hold = 'On Hold';
        var watching = 'Watching';
        var dropped = 'Dropped';
        var plan_to_watch = 'Plan to Watch';

        $("#"+mod_id+ " a").filter(":contains('Watching')").remove()
        $("#"+mod_id+ " a").filter(":contains('Completed')").remove()
        $("#"+mod_id+ " a").filter(":contains('On Hold')").remove()
        $("#"+mod_id+ " a").filter(":contains('Random')").remove()
        $("#"+mod_id+ " a").filter(":contains('Dropped')").remove()
        $("#"+mod_id+ " a").filter(":contains('Plan to Watch')").remove()

        $("#"+mod_id).prepend(
            "<a data-dismiss='modal' class='list-group-item text-light bg-dark modded' onclick='changeCategory(\"" + element_id + "\", \"" + watching + "\", \"" + card_id + "\", \"" + mod_id + "\", \"" + seas_drop_id + "\", \"" + ep_drop_id + "\", \"" + seas_data + "\", \"" + media_list + "\")'>Watching</a>" +
            "<a data-dismiss='modal' class='list-group-item text-light bg-dark modded' onclick='changeCategory(\"" + element_id + "\", \"" + completed + "\", \"" + card_id + "\", \"" + mod_id + "\", \"" + seas_drop_id + "\", \"" + ep_drop_id + "\", \"" + seas_data + "\", \"" + media_list + "\")'>Completed</a>" +
            "<a data-dismiss='modal' class='list-group-item text-light bg-dark modded' onclick='changeCategory(\"" + element_id + "\", \"" + on_hold + "\", \"" + card_id + "\", \"" + mod_id + "\", \"" + seas_drop_id + "\", \"" + ep_drop_id + "\", \"" + seas_data + "\", \"" + media_list + "\")'>On Hold</a>" +
            "<a data-dismiss='modal' class='list-group-item text-light bg-dark modded' onclick='changeCategory(\"" + element_id + "\", \"" + dropped + "\", \"" + card_id + "\", \"" + mod_id + "\", \"" + seas_drop_id + "\", \"" + ep_drop_id + "\", \"" + seas_data + "\", \"" + media_list + "\")'>Dropped</a>" +
            "<a data-dismiss='modal' class='list-group-item text-light bg-dark modded' onclick='changeCategory(\"" + element_id + "\", \"" + plan_to_watch + "\", \"" + card_id + "\", \"" + mod_id + "\", \"" + seas_drop_id + "\", \"" + ep_drop_id + "\", \"" + seas_data + "\", \"" + media_list + "\")'>Plan to Watch</a>"
        );
        $("#" + card_id).prependTo(".d-flex.flex-wrap.RANDOM");
        $("#" + card_id).children('.card-body').show();
        $("#" + card_id).children().children('.btn_bottom_left').show();
        $('.modal').modal("hide");
    }

    if (new_category === 'Dropped') {
        var completed = 'Completed';
        var on_hold = 'On Hold';
        var random = 'Random';
        var watching = 'Watching';
        var plan_to_watch = 'Plan to Watch';

        $("#"+mod_id+ " a").filter(":contains('Watching')").remove()
        $("#"+mod_id+ " a").filter(":contains('Completed')").remove()
        $("#"+mod_id+ " a").filter(":contains('On Hold')").remove()
        $("#"+mod_id+ " a").filter(":contains('Random')").remove()
        $("#"+mod_id+ " a").filter(":contains('Dropped')").remove()
        $("#"+mod_id+ " a").filter(":contains('Plan to Watch')").remove()

        $("#"+mod_id).prepend(
            "<a data-dismiss='modal' class='list-group-item text-light bg-dark modded' onclick='changeCategory(\"" + element_id + "\", \"" + watching + "\", \"" + card_id + "\", \"" + mod_id + "\", \"" + seas_drop_id + "\", \"" + ep_drop_id + "\", \"" + seas_data + "\", \"" + media_list + "\")'>Watching</a>" +
            "<a data-dismiss='modal' class='list-group-item text-light bg-dark modded' onclick='changeCategory(\"" + element_id + "\", \"" + completed + "\", \"" + card_id + "\", \"" + mod_id + "\", \"" + seas_drop_id + "\", \"" + ep_drop_id + "\", \"" + seas_data + "\", \"" + media_list + "\")'>Completed</a>" +
            "<a data-dismiss='modal' class='list-group-item text-light bg-dark modded' onclick='changeCategory(\"" + element_id + "\", \"" + on_hold + "\", \"" + card_id + "\", \"" + mod_id + "\", \"" + seas_drop_id + "\", \"" + ep_drop_id + "\", \"" + seas_data + "\", \"" + media_list + "\")'>On Hold</a>" +
            "<a data-dismiss='modal' class='list-group-item text-light bg-dark modded' onclick='changeCategory(\"" + element_id + "\", \"" + random + "\", \"" + card_id + "\", \"" + mod_id + "\", \"" + seas_drop_id + "\", \"" + ep_drop_id + "\", \"" + seas_data + "\", \"" + media_list + "\")'>Random</a>" +
            "<a data-dismiss='modal' class='list-group-item text-light bg-dark modded' onclick='changeCategory(\"" + element_id + "\", \"" + plan_to_watch + "\", \"" + card_id + "\", \"" + mod_id + "\", \"" + seas_drop_id + "\", \"" + ep_drop_id + "\", \"" + seas_data + "\", \"" + media_list + "\")'>Plan to Watch</a>"
        );
        $("#" + card_id).prependTo(".d-flex.flex-wrap.DROPPED");
        $("#" + card_id).children('.card-body').show();
        $("#" + card_id).children().children('.btn_bottom_left').show();
        $('.modal').modal("hide");
    }

    if (new_category === 'Plan to Watch') {
        var completed = 'Completed';
        var on_hold = 'On Hold';
        var random = 'Random';
        var dropped = 'Dropped';
        var watching = 'Watching';

        $("#"+mod_id+ " a").filter(":contains('Watching')").remove()
        $("#"+mod_id+ " a").filter(":contains('Completed')").remove()
        $("#"+mod_id+ " a").filter(":contains('On Hold')").remove()
        $("#"+mod_id+ " a").filter(":contains('Random')").remove()
        $("#"+mod_id+ " a").filter(":contains('Dropped')").remove()
        $("#"+mod_id+ " a").filter(":contains('Plan to Watch')").remove()

        $("#"+mod_id).prepend(
            "<a data-dismiss='modal' class='list-group-item text-light bg-dark modded' onclick='changeCategory(\"" + element_id + "\", \"" + watching + "\", \"" + card_id + "\", \"" + mod_id + "\", \"" + seas_drop_id + "\", \"" + ep_drop_id + "\", \"" + seas_data + "\", \"" + media_list + "\")'>Watching</a>" +
            "<a data-dismiss='modal' class='list-group-item text-light bg-dark modded' onclick='changeCategory(\"" + element_id + "\", \"" + completed + "\", \"" + card_id + "\", \"" + mod_id + "\", \"" + seas_drop_id + "\", \"" + ep_drop_id + "\", \"" + seas_data + "\", \"" + media_list + "\")'>Completed</a>" +
            "<a data-dismiss='modal' class='list-group-item text-light bg-dark modded' onclick='changeCategory(\"" + element_id + "\", \"" + on_hold + "\", \"" + card_id + "\", \"" + mod_id + "\", \"" + seas_drop_id + "\", \"" + ep_drop_id + "\", \"" + seas_data + "\", \"" + media_list + "\")'>On Hold</a>" +
            "<a data-dismiss='modal' class='list-group-item text-light bg-dark modded' onclick='changeCategory(\"" + element_id + "\", \"" + random + "\", \"" + card_id + "\", \"" + mod_id + "\", \"" + seas_drop_id + "\", \"" + ep_drop_id + "\", \"" + seas_data + "\", \"" + media_list + "\")'>Random</a>" +
            "<a data-dismiss='modal' class='list-group-item text-light bg-dark modded' onclick='changeCategory(\"" + element_id + "\", \"" + dropped + "\", \"" + card_id + "\", \"" + mod_id + "\", \"" + seas_drop_id + "\", \"" + ep_drop_id + "\", \"" + seas_data + "\", \"" + media_list + "\")'>Dropped</a>"
        );
        $("#" + card_id).prependTo(".d-flex.flex-wrap.PLAN.TO.WATCH");
        $("#" + card_id).children('.card-body').hide();
        $("#" + card_id).children().children('.btn_bottom_left').hide();
        $('.modal').modal("hide");
    }

    $body = $("body");
    $categories.isotope('layout');
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


// ---------------- Refresh -----------------
function refresh(element_id, media_list, user_name) {
    $body = $("body");
    $.ajax ({
        type: "POST",
        url: "/refresh_single_element",
        contentType: "application/json",
        data: JSON.stringify({ element_id: element_id, element_type: media_list }),
        dataType: "json",
        beforeSend: function() { $body.addClass("loading"); },
        success: function(response) {
            window.location.replace('/' + media_list + '/' + user_name);
        }
    });
}


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
        opt.text = "Episode " + i;
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

// ------------------- test -------------------
function show_metadata(a, b, c, d, e, f, g, h, i, j, k, l, m, n, o) {
    console.log(a);
    $('#orginal_name').html("<b>Original Name</b>: " +a);
    $('#actors').html("<b>Actors</b>: " +b);
    $('#genres').html("<b>Genres</b>: " +c);
    $('#first_air_date').html("<b>First Air Date</b>: " +d);
    $('#last_air_date').html("<b>Last Air Date</b>: " +e);
    $('#networks').html("<b>Networks</b>: " +f);
    $('#created_by').html("<b>Created By</b>: " +g);
    $('#episode_duration').html("<b>Episode Duration</b>: " +h+ " min");
    $('#total_seasons').html("<b>Total Seasons</b>: " +i);
    $('#total_episodes').html("<b>Total Episodes</b>: " +j);
    $('#episodes_per_season').html("<b>Episodes Per Season</b>: " +k);
    $('#origin_country').html("<b>Origin Country</b>: " +l);
    $('#tmdb_score').html("<b>TMDb Score</b>: " +m+ "/10");
    $('#status').html("<b>Status</b>: " +n);
    $('#synopsis').html("<b>Synopsis</b>: " +o);
}