

// --- Create the buttons category list ------------------------------------
function chargeButtons(card) {
    removeCat();

    let dis_playing = "block;";
    let dis_completed = "block;";
    let dis_endless = "block;";
    let dis_multiplayer = "block;";
    let $card = $('#'+card.id);
    let category = $card.attr('cat');

    if (category === 'Playing') {
        dis_playing = "none;";
    }
    else if (category === 'Completed') {
        dis_completed = "none;";
    }
    else if (category === 'Endless') {
        dis_endless = "none;";
    }
    else if (category === 'Multiplayer') {
        dis_multiplayer = "none;";
    }

    $card.find('.view.overlay').prepend(
        '<a class="card-btn-top-right fas fa-times" onclick="removeCat()"></a>' +
        '<ul class="card-cat-buttons">' +
            '<li class="btn btn-light p-1 m-1 card-btn-mobile" style="display: '+dis_playing+'" ' +
            'onclick="changeCategory(\'Playing\', \''+card.id+'\')">' +
                'Playing' +
            '</li>' +
            '<li class="btn btn-light p-1 m-1 card-btn-mobile" style="display: '+dis_completed+'" ' +
            'onclick="changeCategory(\'Completed\', \''+card.id+'\')">' +
                'Completed' +
            '</li>' +
            '<li class="btn btn-light p-1 m-1 card-btn-mobile" style="display: '+dis_endless+'" ' +
            'onclick="changeCategory(\'Endless\', \''+card.id+'\')">' +
                'Endless' +
            '</li>' +
            '<li class="btn btn-light p-1 m-1 card-btn-mobile" style="display: '+dis_multiplayer+'" ' +
            'onclick="changeCategory(\'Multiplayer\', \''+card.id+'\')">' +
                'Multiplayer' +
            '</li>' +
        "</ul>");

    $card.find('.card-btn-toop-right').hide();
    $card.find('.card-btn-top-left').hide();
    $card.find('.bottom-card-cat').hide();
    $card.find('.bottom-card-info').hide();
    $card.find('.card-img-top').attr('style', 'filter: brightness(20%); height: auto;');
    $card.find('.mask').hide();
}


// --- Change the category -------------------------------------------------
function changeCategory(new_category, card_id) {
    let $card = $('#'+card_id);
    let media_list = $card.attr('values').split('-')[1];
    let element_id = $card.attr('values').split('-')[2];
    let load_img = $card.find('.view.overlay');
    load_img.prepend(Loading());

    $.ajax ({
        type: "POST",
        url: "/change_element_category",
        contentType: "application/json",
        data: JSON.stringify({status: new_category, element_id: element_id, element_type: media_list}),
        dataType: "json",
        success: function() {
            $card.remove();
        },
        error: function () {
            error_ajax_message('Error trying to change the game category. Please try again later.');
        },
        complete: function () {
            removeCat();
            load_img.find('.load-medialist').remove();
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
            'onclick="AddCatUser(\'Playing\', \''+card.id+'\')">' +
                'Playing' +
            '</li>' +
            '<li class="btn btn-light p-1 m-1 card-btn-mobile\" style="display: block;" ' +
            'onclick="AddCatUser(\'Completed\', \''+card.id+'\')">' +
                'Completed' +
            '</li>' +
            '<li class="btn btn-light p-1 m-1 card-btn-mobile\" style="display: block;" ' +
            'onclick="AddCatUser(\'Endless\', \''+card.id+'\')">' +
                'Endless' +
            '</li>' +
            '<li class="btn btn-light p-1 m-1 card-btn-mobile\" style="display: block;" ' +
            'onclick="AddCatUser(\'Multiplayer\', \''+card.id+'\')">' +
                'Multiplayer' +
            '</li>' +
        "</ul>");

    $(card).find('.card-btn-top-left').hide();
    $(card).find('.bottom-card-info').hide();
    $(card).find('.bottom-card-cat').hide();
    $(card).find('.card-img-top').attr('style', 'filter: brightness(20%); height: auto;');
    $(card).find('.mask').hide();
}


// --- Update time played --------------------------------------------------
function updatePlaytime(media_id) {
    $('#'+media_id+'-time-loading').show();
    let hours = $('#'+media_id+'-time_h').val();
    let minutes = $('#'+media_id+'-time_m').val();

    $.ajax ({
        type: "POST",
        url: "/update_playtime",
        contentType: "application/json",
        data: JSON.stringify({hours: hours, min: minutes, media_id: media_id, media_type: 'gameslist' }),
        dataType: "json",
        success: function() {
            $('#'+media_id+'-time-check').show().delay(1500).fadeOut();
        },
        error: function() {
            error_ajax_message('Error updating the time played. Please try again later.');
        },
        complete: function () {
            $('#'+media_id+'-time-loading').hide();
        }
    });
}


// --- Update completion --------------------------------------------------
function updateCompletion(info, element_id) {
    let comp_value = false

    if ($.trim($(info).html()).includes('<strike>')) {
        comp_value = true
    }

    $.ajax ({
        type: "POST",
        url: "/update_completion",
        contentType: "application/json",
        data: JSON.stringify({data: comp_value, element_id: element_id, media_list: 'gameslist' }),
        dataType: "json",
        success: function() {
            if ($.trim($(info).html()).includes('<strike>')) {
                document.getElementById('comp_'+element_id).innerHTML = "<b>100%</b>";
                $(info).attr('style', 'color: goldenrod;');
            } else {
                document.getElementById('comp_'+element_id).innerHTML = "<strike>100%</strike>";
                $(info).attr('style', 'color: lightgray;');
            }
        },
        error: function() {
            error_ajax_message('Error updating the completion of the game. Please try again later.');
        },
        complete: function () {
        }
    });
}
