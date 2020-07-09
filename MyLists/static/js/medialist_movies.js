

// --- Create the cat buttons list -----------------------------------------
function chargeButtons(card) {
    removeCat();
    let completed = "block;";
    let plan_to_watch = "block;";
    let parent_category = $('#'+card.id).parent();

    if (parent_category.hasClass('category-COMPLETED') || parent_category.hasClass('category-ANIMATION')) {
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
    $(card).find('.card-img-top').attr('style', 'filter: brightness(20%); height: auto;');
    $(card).find('.mask').hide();
}


// --- Change the category -------------------------------------------------
function changeCategory(new_category, card_id) {
    let genres = $('#'+card_id).attr('values').split('-')[0];
    let media_list = $('#'+card_id).attr('values').split('-')[1];
    let element_id = $('#'+card_id).attr('values').split('-')[2];
    let parent_cat = $('#'+card_id).parent();
    $('#'+card_id).find('.loading-medialist').show();

        $.ajax ({
        type: "POST",
        url: "/change_element_category",
        contentType: "application/json",
        data: JSON.stringify({status: new_category, element_id: element_id, element_type: media_list}),
        dataType: "json",
        success: function() {
            if (parent_cat.hasClass('category-COMPLETED')) {
                $("#"+card_id).prependTo(".category-PLAN.TO.WATCH");
            }
            else if (parent_cat.hasClass('category-ANIMATION')) {
                $("#"+card_id).prependTo(".category-PLAN.TO.WATCH");
            }
            else {
                if (genres.includes("Animation")) {
                    $("#"+card_id).prependTo(".category-ANIMATION");
                } else {
                    $("#"+card_id).prependTo(".category-COMPLETED");
                }
            }
            $categories.isotope('layout');
        },
        error: function () {
            error_ajax_message('Error changing the media category. Please try again later.');
        },
        complete: function () {
            removeCat();
            $('#'+card_id).find('.loading-medialist').hide();
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
            'onclick="AddCatUser(\'Completed\', \''+card.id+'\')">' +
                'Completed' +
            '</li>' +
            '<li class="btn btn-light p-1 m-1 card-btn-mobile\" style="display: block;" ' +
            'onclick="AddCatUser(\'Plan to Watch\', \''+card.id+'\')">' +
                'Plan to Watch' +
            '</li>' +
        "</ul>");

    $('#'+card.id).find('.card-btn-top-left').hide();
    $('#'+card.id).find('.card-img-top').attr('style', 'filter: brightness(20%); height: auto;');
    $('#'+card.id).find('.mask').hide();
}
