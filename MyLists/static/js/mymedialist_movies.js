

// ------------------------- Create the category list -------------------------
function charge_cat(card, element_id, genres, media_list) {
    remove_cat();

    if ($('#'+card.id).parent().hasClass('category-COMPLETED')) {
        var display_completed = "none;";
        var display_plan_to_watch = "block;";
    }
    else if ($('#'+card.id).parent().hasClass('category-ANIMATION')) {
        var display_completed = "none;";
        var display_plan_to_watch = "block;";
    }
    else {
        var display_completed = "block;";
        var display_plan_to_watch = "none;";
    }

    $(card).find('.view.overlay').prepend (
    "<ul class='card-cat-buttons'>" +
        "<li style='display: " + display_completed + "' class='btn btn-light p-1 m-1 card-btn-mobile' onclick='changeCategory(this,\"" + element_id + "\", \"" + card.id + "\",  \"" + genres + "\", \"" + media_list + "\")'>Completed</li>" +
        "<li style='display: " + display_plan_to_watch + "' class='btn btn-light p-1 m-1 card-btn-mobile' onclick='changeCategory(this, \"" + element_id + "\", \"" + card.id + "\", \"" + genres + "\",  \"" + media_list + "\")'>Plan to Watch</li>" +
    "</ul>");

    $(card).find('.card-btn-top-left').attr('style', 'display: none;');
    $(card).find('.card-btn-top-right').attr('style', 'display: none;');
    $(card).find('.mask').hide();
    $(card).find('.view.overlay').prepend("<a class='card-btn-top-right-2 fas fa-times' onclick='remove_cat()')></a>");
    $(card).find('.card-img-top').attr('style', 'filter: brightness(20%); height: auto;');
}


// ----------------------------- Change category ------------------------------
function changeCategory(new_category, element_id, card_id, genres, media_list) {
    var new_cat = new_category.childNodes[0].data
    remove_cat();

    if ($('#'+card_id).parent().hasClass('category-COMPLETED')) {
        $("#"+card_id).prependTo(".category-PLAN.TO.WATCH");
        new_category = "Plan to Watch";
    }
    else if ($('#'+card_id).parent().hasClass('category-ANIMATION')) {
        $("#"+card_id).prependTo(".category-PLAN.TO.WATCH");
        new_category = "Plan to Watch";
    }
    else {
        if (genres.includes("Animation")) {
            $("#"+card_id).prependTo(".category-ANIMATION");
            new_category = "Completed Animation";
        } else {
            $("#"+card_id).prependTo(".category-COMPLETED");
            new_category = "Completed";
        }
    }

    $categories.isotope('layout');
    $body = $("body");

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


// ------------------------- Movies metadata test -----------------------------
function show_metadata(data) {
    var data = JSON.parse($('#'+data).text());

    $('#original_name').text('');
    if (data.original_language =='ja') {
        $('#modal-title').html(data.name);
    } else {
        $('#modal-title').html(data.original_name);
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
    $('#synopsis').html("<b>Synopsis</b>: " +data.synopsis);
}
