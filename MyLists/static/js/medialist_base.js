

// --- Delete element --------------------------------------------------
function deleteElement(element_id, card_id, media_list) {
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

    $categories.isotope('layout');
}


// --- Remove the category list ----------------------------------------
function removeCat() {
    $('.card-cat-buttons').remove();
    $('.card-btn-top-right-2').remove();
    $('.card-btn-top-left').attr('style', 'display: block;');
    $('.card-btn-top-right').attr('style', 'display: block;');

    $('.seas-eps-box').each(function () {
        if ($(this).parent().parent().parent()[0].className === 'row category-PLAN TO WATCH') {
            $(this).attr('style', 'display: none;');
        } else {
            $(this).attr('style', 'display: inline-block;');
        }
    });

    $('.card-img-top').attr('style', 'filter: brightness(100%); height: auto;');
    $('.mask').show();
}


// --- Search by Title or Actor ----------------------------------------
function searchElement() {
    let input, cat, filter, cards, cardContainer, title, i, l;
    input = document.getElementById("searchInput");
    cat = document.getElementsByClassName("search-select")[0].value;
    filter = input.value.toUpperCase();
    cardContainer = document.getElementById("categories-iso");
    cards = cardContainer.getElementsByClassName("card-container");
    l = cards.length;
    for (i = 0; i < l; i++) {
        title = cards[i].querySelector(".font-mask");
        original_title = cards[i].querySelector(".by-original-title");
        actors = cards[i].querySelector(".by-actor");
        genres = cards[i].querySelector(".by-genre");
        if (title.innerText.toUpperCase().indexOf(filter) > -1 && (cat === 'Titles' || cat === 'All')) {
            cards[i].style.display = "";
        } else if (original_title.innerText.toUpperCase().indexOf(filter) > -1 && (cat === 'Titles' || cat === 'All')) {
            cards[i].style.display = "";
        } else if (actors.innerText.toUpperCase().indexOf(filter) > -1 && (cat === 'Actors' || cat === 'All')) {
            cards[i].style.display = "";
        } else if (genres.innerText.toUpperCase().indexOf(filter) > -1 && (cat === 'Genres' || cat === 'All')) {
            cards[i].style.display = "";
        } else {
            cards[i].style.display = "none";
        }
    }

    $categories.isotope('layout');
}


// --- Add media to favorite -------------------------------------------
function addFavorite(element_id, media_type) {
    let favorite

    if ($('#fav-'+element_id).hasClass('far')) {
        $('#fav-'+element_id).removeClass('far card-btn-bottom-left').addClass('fas card-favorite')
        $('#fav-'+element_id).attr('style', 'color: darkgoldenrod;')
        favorite = true
    } else {
        $('#fav-'+element_id).removeClass('fas card-favorite').addClass('far card-btn-bottom-left')
        $('#fav-'+element_id).attr('style', 'color: white;')
        favorite = false
    }

    $body = $("body");
    $.ajax ({
        type: "POST",
        url: "/add_favorite",
        contentType: "application/json",
        data: JSON.stringify({ element_id: element_id, element_type: media_type, favorite: favorite }),
        dataType: "json",
        success: function(response) {
            console.log("ok");
        }
    });
}


// --- Show/Hide common media ------------------------------------------
function HideCommon() {
    if ($('#SharedMedia').prop("checked") == true) {
        $('.card-ribbon').parent().parent().parent().hide();
    } else if ($('#SharedMedia').prop("checked") == false && $('#ShowFavorites').prop("checked") == true) {
        $('.card-ribbon').parent().parent().parent().show();
        $('.far.fa-star').parent().parent().parent().hide();
    } else if ($('#SharedMedia').prop("checked") == false && $('#ShowFavorites').prop("checked") == false) {
        $('.card-ribbon').parent().parent().parent().show();
    }
    $categories.isotope('layout');
}


// --- Show/Hide favorites media ---------------------------------------
function ShowFavorites() {
    if ($('#ShowFavorites').prop("checked") == true) {
        $('.far.fa-star').parent().parent().parent().hide();
    } else if ($('#ShowFavorites').prop("checked") == false && $('#SharedMedia').prop("checked") == true) {
        $('.far.fa-star').parent().parent().parent().show();
        $('.card-ribbon').parent().parent().parent().hide();
    } else if ($('#ShowFavorites').prop("checked") == false && $('#SharedMedia').prop("checked") == false) {
        $('.far.fa-star').parent().parent().parent().show();
    }

    $categories.isotope('layout');
}


// --- Add the category to the user (from other list) ------------------
function AddCatUser(cat, card_id, element_id, media_type) {
    var add_cat = cat.childNodes[0].data

    $body = $("body");
    $.ajax ({
        type: "POST",
        url: "/add_element",
        contentType: "application/json",
        data: JSON.stringify({element_cat: add_cat, element_id: element_id, element_type: media_type}),
        dataType: "json",
        success: function(response) {
            console.log("ok");
        }
    });

    removeCat();
    $("#"+card_id).children().children('div[class="view overlay"]').append("<div class='card-ribbon'></div>");
    $("#"+card_id).children().children().children().remove(".card-btn-top-left.fas.fa-plus.text-light");
}


// --- Tooltip ---------------------------------------------------------
$(document).ready(function() {
    $body = $("body");
    $body.tooltip();
    $(function () {
        $('[data-toggle="tooltip"]').tooltip()
    })
});


// --- Isotopes --------------------------------------------------------
let $categories = $('.categories-iso').isotope({
    itemSelector: '.categories',
    layoutMode: 'vertical',
    onLayout: function() {
        $window.trigger("scroll");
    }
});
$("img.lazyload").lazyload({
    failure_limit : Math.max($("img.lazyload").length-1, 0)
});

$('.filters-button-group').on('click', 'button', function() {
    var filterValue = $(this).attr('data-filter');
    $categories.isotope({ filter: filterValue });
});

$('.filters-button-group').each(function(i, buttonGroup) {
    var $buttonGroup = $(buttonGroup);
    $buttonGroup.on('click', 'button', function() {
        $buttonGroup.find('.btn-selected').addClass('btn-header');
        $buttonGroup.find('.btn-selected').removeClass('btn-selected');
        $(this).addClass('btn-selected');
        $(this).removeClass('btn-header');
    });
});
$categories.isotope('layout');


// --- Row gutters -----------------------------------------------------
(function($) {
    var $window = $(window),
        $row = $('.row');

    function resize() {
        if ($window.width() < 1025) {
            return $row.addClass('no-gutters');
        }
        $row.removeClass('no-gutters');
    }
    $window.resize(resize).trigger('resize');
    $categories.isotope('layout');
})(jQuery);


$categories.isotope('layout');
