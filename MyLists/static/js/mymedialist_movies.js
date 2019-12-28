

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


// ------------------------- Movies metadata test --------------------------
function show_metadata(data) {
    $categories.isotope('layout');
    $('#original_name').text('');
    $('#modal_title').html(data.name);
    if (data.name != data.original_name) {
        $('#original_name').html("<b>Original Name</b>: " +data.original_name);
    }
    $('#release_date').html("<b>Release Date</b>: " +data.release_date);
    $('#actors').html("<b>Actors</b>: " +data.actors);
    $('#genres').html("<b>Genres</b>: " +data.genres);
    $('#budget').html("<b>Budget</b>: " +data.budget.toLocaleString("en")+ " $");
    $('#revenue').html("<b>Revenue</b>: " +data.revenue.toLocaleString("en")+ " $");
    $('#runtime').html("<b>Runtime</b>: " +data.runtime+ " min");
    $('#original_language').html("<b>Original Language</b>: " +data.original_language);
    $('#tmdb_score').html("<b>TMDb Score</b>: " +data.vote_average+ "/10 &nbsp;(" +data.vote_count.toLocaleString("en")+ " votes)");
    $('#tagline').html("<b>Tagline</b>: " +data.tagline);
    $('#prod_companies').html("<b>Prod. Companies</b>: " +data.prod_companies);
    $('#synopsis').html("<b>Synopsis</b>: " +data.synopsis);
}
