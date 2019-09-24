
// ------------- Delete element -------------
function delete_element(element_id, card_id, element_name, media_list) {
    if (!confirm("Are you sure you want to delete this from your list?")) {
        return false;
    }

    $categories.isotope('layout');
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


// ---------- Show/hide all score -----------
function all_scores() {
    if ($('#all_scores').text() == 'Show scores') {
        $('div[id^="footer_"]').attr('class', 'card-footer text-muted text-center p-0');
        $('.card').attr('class', 'card bg-transparent m-l-10 m-r-10 m-b-15 m-t-20');
        $("#all_scores").text('Hide scores');
    } else {
        $('div[id^="footer_"]').attr('class', 'd-none footer_score');
        $('.card').attr('class', 'card bg-transparent m-l-10 m-r-10 m-b-40 m-t-20');
        $("#all_scores").text('Show scores');
    }
}


// --------------- Edit score ---------------
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


// ---------------- Add score ---------------
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


// --------------- Tooltip ------------------
$('.tooltip').tooltip();
$(function () {
    $('[data-toggle="tooltip"]').tooltip()
})


// --------------- Isotope categories ------------------
var $categories = $('.categories-iso').isotope({
    itemSelector: '.categories',
    layoutMode: 'vertical'
});

//bind filter button click
$('.filters-button-group').on('click', 'button', function() {
    var filterValue = $(this).attr('data-filter');
    $categories.isotope({ filter: filterValue });
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


//// -------- Isotope elements (movies/series/anime) -----------
//var $completed = $('.COMPLETED').isotope({
//    itemSelector: '.card-COMPLETED',
//    layoutMode: 'fitRows'
//});
//
////bind filter select click
//$('.filters-select-group-COMPLETED').on('click', 'option', function() {
//    var filterValue = $(this).attr('data-filter');
//    $completed.isotope({ filter: filterValue });
//});
//
//
//// -------- Isotope elements (movies/series/anime) -----------
//var $plantowatch = $('.PLAN_TO_WATCH').isotope({
//    itemSelector: '.card-PLAN_TO_WATCH',
//    layoutMode: 'fitRows'
//});
//
////bind filter select click
//$('.filters-select-group-PLAN_TO_WATCH').on('click', 'option', function() {
//    var filterValue = $(this).attr('data-filter');
//    $plantowatch.isotope({ filter: filterValue });
//});


//function deleted(card_id, category) {
//    if (category == 'COMPLETED') {
//        $completed.isotope('remove', card_id).isotope('layout');
//    } else {
//        $plantowatch.isotope('remove', card_id).isotope('layout');
//    }
//}
//
//function Category(card_id, category) {
//    if (category == 'plantowatch') {
//        var $card = $('#'+card_id);
//        $card.attr('style', 'border-radius: 5px;');
//        $plantowatch.prepend($card).isotope('prepended', $card);
//    } else {
//        console.log("test");
//    }
//}


$categories.isotope('layout');


function searchElement() {
    var input, filter, cards, cardContainer, title, i;
    input = document.getElementById("myElementFilter");
    filter = input.value.toUpperCase();
    cardContainer = document.getElementById("categories-iso");
    cards = cardContainer.getElementsByClassName("card");
    for (i = 0; i < cards.length; i++) {
        title = cards[i].querySelector(".font-mask");
        if (title.innerText.toUpperCase().indexOf(filter) > -1) {
            cards[i].style.display = "";
        } else {
            cards[i].style.display = "none";
        }
    }
    $categories.isotope('layout');
}





