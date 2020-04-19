

// --- Add the media to the user ---------------------------
function addToUser(element_id, media_type) {
    $('#your-medialist-data').show();
    $('#addlist').hide();

    $body = $("body");
    $.ajax ({
        type: "POST",
        url: "/add_element",
        contentType: "application/json",
        data: JSON.stringify({ element_id: element_id, element_type: media_type, element_cat: 'Watching',
            from_other_list: false }),
        dataType: "json",
        success: function(response) {
            console.log("ok");
        }
    });
}


// --- Set media to favorite -------------------------------
function addFavorite(element_id, media_type) {
    let favorite;

    if ($('#favorite').hasClass('far')) {
        $('#favorite').addClass('fas').removeClass('far');
        $('#alert').addClass('alert-success').removeClass('alert-warning');
        $('#alert').attr('style', 'display: block;');
        $('#alert').html('');
        $('#alert').html('<i class="fas fa-check m-r-5"></i> Added to favorite');
        $('#alert').delay(800).fadeOut('slow');
        favorite = true;
    }
    else {
        $('#favorite').addClass('far').removeClass('fas');
        $('#alert').addClass('alert-warning').removeClass('alert-success');
        $('#alert').attr('style', 'display: block;');
        $('#alert').html('');
        $('#alert').html('<i class="fas fa-times m-r-5"></i> Removed from favorite');
        $('#alert').delay(800).fadeOut('slow');
        favorite = false;
    }

    $body = $("body");
    $.ajax ({
        type: "POST",
        url: "/add_favorite",
        contentType: "application/json",
        data: JSON.stringify({ element_id: element_id, element_type: media_type, favorite: favorite }),
        dataType: "json",
        success: function(response) {
            console.log("ok");
        }
    });
}


// --- Change the category ---------------------------------
function changeCategory(element_id, cat_selector, seas_data, media_list) {
    let new_cat = cat_selector.options[cat_selector.selectedIndex].value;

    $('#season-row').show();
    $('#episode-row').show();

    if (new_cat === 'Completed') {
        let season_data = JSON.parse("["+seas_data+"]");
        let episode_drop = document.getElementById('episode-dropdown');

        let seasons_length = $('#season-dropdown').children('option').length;
        let seasons_index = (seasons_length - 1);
        $('#season-dropdown').prop('selectedIndex', seasons_index);

        episode_drop.length = 1;

        for (i = 2; i <= season_data[0][seasons_index]; i++) {
            let opt = document.createElement("option");
            opt.className = "";
            if (i <= 9) {
                opt.text = i;
            } else {
                opt.text = i;
            }
            episode_drop.appendChild(opt);
        }
        $('#episode-dropdown').prop('selectedIndex', season_data[0][seasons_index]-1);
    }
    else if (new_cat === 'Random') {
        $('#season-row').hide();
        $('#episode-row').hide();
    }
    else if (new_cat === 'Plan to Watch') {
        $('#season-row').hide();
        $('#episode-row').hide();
    }

    $body = $("body");
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


// --- Update season ---------------------------------------
function updateSeason(element_id, value, seas_data, media_list) {
    let selected_season = value.selectedIndex;
    let episode_drop = document.getElementById('episode-dropdown');
    let season_data = JSON.parse("["+seas_data+"]");

    episode_drop.length = 1;
    for (i = 2; i <= season_data[0][selected_season]; i++) {
        let opt = document.createElement("option");
        opt.className = "";
        if (i <= 9) {
                opt.text = i;
            } else {
                opt.text = i;
            }
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


// --- Update episode --------------------------------------
function updateEpisode(element_id, episode, media_list) {
    let selected_episode = episode.selectedIndex;

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
