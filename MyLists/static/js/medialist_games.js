

// --- Create the cat buttons list -----------------------------------------
function chargeButtons(card) {
    removeCat();

    let completed = "block;";
    let plan_to_watch = "block;";
    let category = $('#'+card.id).attr('cat');

    if (category === 'Completed' || category === 'Completed Animation') {
        completed = "none;";
    } else {
        plan_to_watch = "none;";
    }

    $(card).find('.view.overlay').prepend(
        '<a class="card-btn-top-right fas fa-times" onclick="removeCat()"></a>' +
        '<ul class="card-cat-buttons">' +
            '<li class="btn btn-light p-1 m-1 card-btn-mobile" style="display: ' + completed +'" ' +
            'onclick="changeCategory(\'Completed\', \''+card.id+'\')">' +
                'Completed' +
            '</li>' +
            '<li class="btn btn-light p-1 m-1 card-btn-mobile" style="display: ' + plan_to_watch +'" ' +
            'onclick="changeCategory(\'Plan to Watch\', \''+card.id+'\')">' +
                'Plan to Watch' +
            '</li>' +
        "</ul>");

    $(card).find('.card-btn-top-left').hide();
    $(card).find('.card-btn-toop-right').hide();
    $(card).find('.bottom-card-cat-movie').hide();
    $(card).find('.card-img-top').attr('style', 'filter: brightness(20%); height: auto;');
    $(card).find('.mask').hide();
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
            error_ajax_message('Error trying to change the media category. Please try again later.');
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
    let $card = $('#'+card.id)

    $(card).find('.view.overlay').prepend(
        '<a class="card-btn-top-right fas fa-times" onclick="removeCat()"></a>' +
        '<ul class="card-cat-buttons">' +
            '<li class="btn btn-light p-1 m-1 card-btn-mobile\" style="display: block;" ' +
            'onclick="AddCatUser(\'Completed\', \''+card.id+'\')">' +
                'Completed' +
            '</li>' +
            '<li class="btn btn-light p-1 m-1 card-btn-mobile\" style="display: block;" ' +
            'onclick="AddCatUser(\'Plan to Watch\', \''+card.id+'\')">' +
                'Plan to Watch' +
            '</li>' +
        "</ul>");

    $card.find('.card-btn-top-left').hide();
    $card.find('.bottom-card-cat-movie').hide();
    $card.find('.card-img-top').attr('style', 'filter: brightness(20%); height: auto;');
    $card.find('.mask').hide();
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
