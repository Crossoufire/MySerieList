// ----------- Change category --------------
function changeCategory(element_id, new_category, card_id, mod_id, media_list) {
    if (new_category === 'Completed') {
        var plan_to_watch = 'Plan to Watch';

        $("#"+mod_id+ " a").filter(":contains('Completed')").remove()
        $("#"+mod_id+ " a").filter(":contains('Plan to Watch')").remove()

        $("#"+mod_id).prepend(
            "<a data-dismiss='modal' class='list-group-item text-light bg-dark modded' onclick='changeCategory(\"" + element_id + "\", \"" + plan_to_watch + "\", \"" + card_id + "\", \"" + mod_id + "\", \"" + media_list + "\")'>Plan to Watch</a>"
        );
        $("#" + card_id).prependTo(".COMPLETED");
        $('.modal').modal("hide");
    }

    if (new_category === 'Plan to Watch') {
        var completed = 'Completed';

        $("#"+mod_id+ " a").filter(":contains('Completed')").remove()
        $("#"+mod_id+ " a").filter(":contains('Plan to Watch')").remove()

        $("#"+mod_id).prepend(
            "<a data-dismiss='modal' class='list-group-item text-light bg-dark modded' onclick='changeCategory(\"" + element_id + "\", \"" + completed + "\", \"" + card_id + "\", \"" + mod_id + "\", \"" + media_list + "\")'>Completed</a>"
        );
        $("#" + card_id).prependTo(".PLAN_TO_WATCH");
        $('.modal').modal("hide");
    }

    $body = $("body");
    $grid.isotope('layout');
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

// ------------- Delete element -------------
function delete_element(element_id, card_id, element_name, media_list) {
    if (!confirm("Are you sure you want to delete this from your list?")) {
        return false;
    }

    $("#"+card_id).remove();
    $body = $("body");
    $.ajax ({
        type: "POST",
        url: "/delete_element",
        contentType: "application/json",
        data: JSON.stringify({ delete: element_id, element_type: media_list }),
        dataType: "json",
        success: function(response) {
            console.log("ok");
        }
    });
}

// ------------ Show all score --------------
function show_all_score() {
    var show = document.getElementById('show_all');
    var hide = document.getElementById('hide_all');
    $('div[id^="footer_"]').attr('class', 'card-footer text-muted text-center p-0');
    hide.className = "fas fa-eye-slash text-light m-r-5";
    show.className = "d-none";
    $('#show_hide').text('Hide scores');
    $('#score_container').attr('onclick', 'hide_all_score()');
    $('.card').attr('class', 'card bg-transparent m-l-10 m-r-10 m-b-15 m-t-20');
}

// ------------ Hide all score --------------
function hide_all_score() {
    var hide = document.getElementById('hide_all');
    var show = document.getElementById('show_all');
    $('div[id^="footer_"]').attr('class', 'd-none footer_score');
    hide.className = "d-none";
    show.className = "fas fa-eye text-light m-r-5";
    $('#show_hide').text('Show scores');
    $('#score_container').attr('onclick', 'show_all_score()');
    $('.card').attr('class', 'card bg-transparent m-l-10 m-r-10 m-b-40 m-t-20');
}

// -------------- Show score ----------------
function show_score(footer_id, card_id) {
    var score = document.getElementById(footer_id);

    if (score.className === "d-none footer_score"){
        score.className = "card-footer text-muted text-center p-0";
        $(card_id).attr('class', 'card bg-transparent m-l-10 m-r-10 m-b-15 m-t-20');
    } else {
        score.className = "d-none footer_score";
        $(card_id).attr('class', 'card bg-transparent m-l-10 m-r-10 m-b-40 m-t-20');
    }
}


// --------------- Isotope categories ------------------
var $grid = $('.grid-iso').isotope({
    itemSelector: '.category',
    layoutMode: 'masonry'
});

// bind filter button click
$('.filters-button-group').on('click', 'button', function() {
    var filterValue = $(this).attr('data-filter');
    console.log(filterValue);
    $grid.isotope({ filter: filterValue });
});

// change the class on the selected button
$('.filters-button-group').each(function(i, buttonGroup) {
    var $buttonGroup = $(buttonGroup);
    $buttonGroup.on('click', 'button', function() {
        $buttonGroup.find('.btn-warning').addClass('btn-light');
        $buttonGroup.find('.btn-warning').removeClass('btn-warning');
        $(this).addClass('btn-warning');
        $(this).removeClass('btn-light');
    });
});


 $grid.isotope('layout');