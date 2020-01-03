

// ----------------------------- Delete element -----------------------------
function delete_element(element_id, card_id, media_list) {
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
    $categories.isotope('layout');
}


// ---------------------- Remove the category list --------------------------
function remove_cat() {
    $('.card-cat-buttons').remove();
    $('.card-btn-top-right-2').remove();
    $('.card-btn-top-left').attr('style', 'display: block;');
    $('.card-btn-top-right').attr('style', 'display: block;');
    $('.seas-eps-box').attr('style', 'display: inline-block;');
    $('.card-img-top').attr('style', 'filter: brightness(100%);');
    $('.mask').show();
    $categories.isotope('layout');
}


// ----------------------- Search by Title or Actor -------------------------
function searchElement() {
    var input, filter, cards, cardContainer, title, i, l;
    input = document.getElementById("searchInput");
    filter = input.value.toUpperCase();
    cardContainer = document.getElementById("categories-iso");
    cards = cardContainer.getElementsByClassName("card");
    l = cards.length;
    for (i = 0; i < l; i++) {
        title = cards[i].querySelector(".font-mask");
        original_title = cards[i].querySelector(".original-title");
        actors = cards[i].querySelector(".actors-yes");
        genres = cards[i].querySelector(".genre-yes");
        if (title.innerText.toUpperCase().indexOf(filter) > -1) {
            cards[i].style.display = "";
        } else if (original_title.innerText.toUpperCase().indexOf(filter) > -1) {
            cards[i].style.display = "";
        } else if (actors.innerText.toUpperCase().indexOf(filter) > -1) {
            cards[i].style.display = "";
        } else if (genres.innerText.toUpperCase().indexOf(filter) > -1) {
            cards[i].style.display = "";
        } else {
            cards[i].style.display = "none";
        }
    }
    $categories.isotope('layout');
}


// ------------------------------- Tooltip ----------------------------------
$('.tooltip').tooltip();
$(function () {
    $('[data-toggle="tooltip"]').tooltip()
})


// ------------------------------- Slider ----------------------------------
var slider = document.getElementById("myRange");
var output = document.getElementsByClassName("card");

function resetRange() {
    $(output).attr('style', 'width: 198px;');
    slider.value = 198;
    $categories.isotope('layout');
}

// Update the current slider value
slider.oninput = function() {
    $(output).attr('style', 'width: ' +slider.value+ 'px;');
    $categories.isotope('layout');
}


// ------------------------- Isotope categories -----------------------------
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

$categories.isotope('layout');
