
// ----------- Change category --------------
function changeCategory(card_id, element_id, genres, media_list) {

    if ($('#'+card_id).parent().hasClass('COMPLETED')) {
        $("#" + card_id).prependTo(".d-flex.PLAN.TO.WATCH");
        new_category = "Plan to Watch";
    }
    else if ($('#'+card_id).parent().hasClass('ANIMATION')) {
        $("#" + card_id).prependTo(".d-flex.flex-wrap.PLAN.TO.WATCH");
        new_category = "Plan to Watch";
    }
    else {
        if (genres.includes("Animation")) {
            $("#" + card_id).prependTo(".d-flex.flex-wrap.ANIMATION");
            new_category = "Completed Animation";
        } else {
            $("#" + card_id).prependTo(".d-flex.flex-wrap.COMPLETED");
            new_category = "Completed";
        }
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