

// --- Create the buttons category list ------------------------------------
function chargeButtons(card) {
    removeCat();

    let display_watching = "block;";
    let display_completed = "block;";
    let display_on_hold = "block;";
    let display_random = "block;";
    let display_dropped = "block;";
    let display_plan_to_watch = "block;";

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
        '<a class="card-btn-top-right fas fa-times" onclick="removeCat()"></a>' +
        '<ul class="card-cat-buttons">' +
            '<li class="btn btn-light p-1 m-1 card-btn-mobile" style="display: '+display_watching+'" ' +
            'onclick="changeCategory(\'Watching\', \''+card.id+'\')">' +
                'Watching' +
            '</li>' +
            '<li class="btn btn-light p-1 m-1 card-btn-mobile" style="display: '+display_completed+'" ' +
            'onclick="changeCategory(\'Completed\', \''+card.id+'\')">' +
                'Completed' +
            '</li>' +
            '<li class="btn btn-light p-1 m-1 card-btn-mobile" style="display: '+display_on_hold+'" ' +
            'onclick="changeCategory(\'On Hold\', \''+card.id+'\')">' +
                'On Hold' +
            '</li>' +
            '<li class="btn btn-light p-1 m-1 card-btn-mobile" style="display: '+display_random+'" ' +
            'onclick="changeCategory(\'Random\', \''+card.id+'\')">' +
                'Random' +
            '</li>' +
            '<li class="btn btn-light p-1 m-1 card-btn-mobile" style="display: '+display_dropped+'" ' +
            'onclick="changeCategory(\'Dropped\', \''+card.id+'\')">' +
                'Dropped' +
            '</li>' +
            '<li class="btn btn-light p-1 m-1 card-btn-mobile" style="display: '+display_plan_to_watch+'" ' +
            'onclick="changeCategory(\'Plan to Watch\', \''+card.id+'\')">' +
                'Plan to Watch' +
            '</li>' +
        "</ul>");

    $(card).find('.card-btn-toop-right').hide();
    $(card).find('.card-btn-top-left').hide();
    $(card).find('.bottom-card-info').hide();
    $(card).find('.card-img-top').attr('style', 'filter: brightness(20%); height: auto;');
    $(card).find('.mask').hide();
}


// --- Change the category -------------------------------------------------
function changeCategory(new_category, card_id) {
    removeCat();
    let seas_data = $('#'+card_id).attr('values').split('-')[0];
    let media_list = $('#'+card_id).attr('values').split('-')[1];
    let element_id = $('#'+card_id).attr('values').split('-')[2];
    $('#'+card_id).find('.loading-medialist').show();

    if ($('#'+card_id).parent()[0].className === 'row category-PLAN TO WATCH' ||
        $('#'+card_id).parent()[0].className === 'row category-RANDOM') {
        let season_data = JSON.parse("[" + seas_data + "]");
        let episode_drop = $('#E_'+element_id);
        $('#S_'+element_id).prop('selectedIndex', 0);

        episode_drop[0].length = 1;

        for (let i = 2; i <= season_data[0][0]; i++) {
            let opt = document.createElement("option");
            opt.className = "card-opt-box";
            if (i <= 9) {
                opt.innerHTML = "&nbsp;E0"+i+"&nbsp;";
            } else {
                opt.innerHTML = "&nbsp;E"+i+"&nbsp;";
            }
            episode_drop[0].appendChild(opt);
        }
        $('#E_'+element_id).prop('selectedIndex', 0);
    }

    $.ajax ({
        type: "POST",
        url: "/change_element_category",
        contentType: "application/json",
        data: JSON.stringify({status: new_category, element_id: element_id, element_type: media_list }),
        dataType: "json",
        success: function() {
            $('#rew_'+element_id).text(0).show();
            $('#rew_'+element_id).parent().hide();

            if (new_category === 'Watching') {
                $("#"+card_id).prependTo(".category-WATCHING");
            }
            else if (new_category === 'Completed') {
                $("#"+card_id).prependTo(".category-COMPLETED");
                $('#rew_'+element_id).parent().show();

                let season_data = JSON.parse("[" + seas_data + "]");
                let episode_drop = $('#E_'+element_id);
                let seasons_length = $('#S_'+element_id).children('option').length;
                let seasons_index = (seasons_length - 1);
                $('#S_'+element_id).prop('selectedIndex', seasons_index);

                episode_drop[0].length = 1;

                for (let i = 2; i <= season_data[0][seasons_index]; i++) {
                    let opt = document.createElement("option");
                    opt.className = "card-opt-box";
                    if (i <= 9) {
                        opt.innerHTML = "&nbsp;E0"+i+"&nbsp;";
                    } else {
                        opt.innerHTML = "&nbsp;E"+i+"&nbsp;";
                    }
                    episode_drop[0].appendChild(opt);
                }
                $('#E_'+element_id).prop('selectedIndex', season_data[0][seasons_index]-1);
            }
            else if (new_category === 'On Hold') {
                $("#"+card_id).prependTo(".category-ON.HOLD");
            }
            else if (new_category === 'Random') {
                $("#"+card_id).prependTo(".category-RANDOM");
            }
            else if (new_category === 'Dropped') {
                $("#"+card_id).prependTo(".category-DROPPED");
            }
            else {
                $("#"+card_id).prependTo(".category-PLAN.TO.WATCH");
            }
            removeCat();
            $categories.isotope('layout');
        },
        error: function () {
            error_ajax_message('Error changing the category of the media. PLease try again later.')
        },
        complete: function () {
            $('#'+card_id).find('.loading-medialist').hide();
        }
    });
}


// --- Update episode ------------------------------------------------------
function updateEpisode(element_id, episode, media_list) {
    let selected_episode = episode.selectedIndex

    $.ajax ({
        type: "POST",
        url: "/update_element_episode",
        contentType: "application/json",
        data: JSON.stringify({episode: selected_episode, element_id: element_id, element_type: media_list }),
        dataType: "json",
        success: function() {

        },
        error: function () {
            error_ajax_message("Error updating the media's episode. Please try again later.")
        }
    });
}


// --- Update season -------------------------------------------------------
function updateSeason(element_id, value) {
    let selected_season = value.selectedIndex;
    let seas_data = $('#card_'+element_id).attr('values').split('-')[0];
    let media_list = $('#card_'+element_id).attr('values').split('-')[1];

    $.ajax ({
        type: "POST",
        url: "/update_element_season",
        contentType: "application/json",
        data: JSON.stringify({season: selected_season, element_id: element_id, element_type: media_list }),
        dataType: "json",
        success: function() {
            let episode_drop = $('#E_'+element_id);
            let season_data = JSON.parse("[" + seas_data + "]");

            episode_drop[0].length = 1;

            for (let i = 2; i <= season_data[0][selected_season]; i++) {
                let opt = document.createElement("option");
                opt.className = "seas-eps-drop-options";
                if (i <= 9) {
                        opt.innerHTML = "E0"+i;
                    } else {
                        opt.innerHTML = "E"+i;
                    }
                episode_drop[0].appendChild(opt);
            }
        },
        error: function () {
            error_ajax_message('Error updating the season of the media. Please try again later.')
        }
    });
}


// --- Charge the categories buttons from other lists ----------------------
function ChargeButtonsOther(card) {
    removeCat();

    $(card).find('.view.overlay').prepend(
        '<a class="card-btn-top-right fas fa-times" onclick="removeCat()"></a>' +
        '<ul class="card-cat-buttons">' +
            '<li class="btn btn-light p-1 m-1 card-btn-mobile\" style="display: block;" ' +
            'onclick="AddCatUser(\'Watching\', \''+card.id+'\')">' +
                'Watching' +
            '</li>' +
            '<li class="btn btn-light p-1 m-1 card-btn-mobile\" style="display: block;" ' +
            'onclick="AddCatUser(\'Completed\', \''+card.id+'\')">' +
                'Completed' +
            '</li>' +
            '<li class="btn btn-light p-1 m-1 card-btn-mobile\" style="display: block;" ' +
            'onclick="AddCatUser(\'On Hold\', \''+card.id+'\')">' +
                'On Hold' +
            '</li>' +
            '<li class="btn btn-light p-1 m-1 card-btn-mobile\" style="display: block;" ' +
            'onclick="AddCatUser(\'Random\', \''+card.id+'\')">' +
                'Random' +
            '</li>' +
            '<li class="btn btn-light p-1 m-1 card-btn-mobile\" style="display: block;" ' +
            'onclick="AddCatUser(\'Dropped\', \''+card.id+'\')">' +
                'Dropped' +
            '</li>' +
            '<li class="btn btn-light p-1 m-1 card-btn-mobile\" style="display: block;" ' +
            'onclick="AddCatUser(\'Plan to Watch\', \''+card.id+'\')">' +
                'Plan to Watch' +
            '</li>' +
        "</ul>");

    $(card).find('.card-btn-top-left').hide();
    $(card).find('.bottom-card-info').hide();
    $(card).find('.card-img-top').attr('style', 'filter: brightness(20%); height: auto;');
    $(card).find('.mask').hide();
}
