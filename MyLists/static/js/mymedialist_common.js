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
            window.location.replace('/' + media_list + user_name);
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

// --------------- Edit score -----------------
function edit_score(edit_id, new_id) {
    var edit = document.getElementById(edit_id);

    if (edit.className === "d-none"){
        edit.className = "visible";
        document.getElementById(new_id).innerHTML = "";
        $(edit).val('');
        $(edit).focus();
    } else {
        edit.className = "d-none";
    }
}

// ---------------- Add score -----------------
function add_score(new_score, edit_id, element_id, media_list) {
    var new_sc = document.getElementById(new_score);
    var edit_score_value = document.getElementById(edit_id).value;
    var edit_score = document.getElementById(edit_id);

    if (event.which == 13 || event.keyCode == 13) {
        if (edit_score_value > 10 || edit_score_value < 0) {
            window.alert("Your number must be between 0-10");
        } else if (isNaN(edit_score_value) == true) {
            window.alert("Your must enter a number between 0-10");
        } else if ($.trim($(edit_score).val()).length == 0) {
            $(new_sc).text("-");
            edit_score.className = "d-none";
        } else {
            edit_score.className = "d-none";
            $(new_sc).text(edit_score_value);

            $body = $("body");
            $.ajax ({
                type: "POST",
                url: "/add_score_element",
                contentType: "application/json",
                data: JSON.stringify({score_val: edit_score_value, element_id: element_id, element_type: media_list }),
                dataType: "json",
                success: function(response) {
                    console.log('ok'); }
            });
            return false;
        }
        return true;
    }
}

// --------------- tooltip ------------------
$('.tooltip').tooltip();
$(function () {
    $('[data-toggle="tooltip"]').tooltip()
})