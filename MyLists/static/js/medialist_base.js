

// --- Delete element --------------------------------------------------
function deleteElement(element_id, card_id, media_list) {
    if (!confirm('Delete this media from your list?')) {
        return false;
    }

    $.ajax ({
        type: "POST",
        url: "/delete_element",
        contentType: "application/json",
        data: JSON.stringify({ delete: element_id, element_type: media_list }),
        dataType: "json",
        success: function() {
            $("#"+card_id).remove();
        },
        error: function () {
            error_ajax_message('Error trying to remove the media. Please try again later.')
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
        }
        else {
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
        let original_title = cards[i].querySelector(".by-original-title");
        let actors = cards[i].querySelector(".by-actor");
        let genres = cards[i].querySelector(".by-genre");
        let director = cards[i].querySelector(".by-director");
        if (title.innerText.toUpperCase().indexOf(filter) > -1 && (cat === 'Titles' || cat === 'All')) {
            cards[i].style.display = "";
        }
        else if (original_title.innerText.toUpperCase().indexOf(filter) > -1 && (cat === 'Titles' || cat === 'All')) {
            cards[i].style.display = "";
        }
        else if (actors.innerText.toUpperCase().indexOf(filter) > -1 && (cat === 'Actors' || cat === 'All')) {
            cards[i].style.display = "";
        }
        else if (genres.innerText.toUpperCase().indexOf(filter) > -1 && (cat === 'Genres' || cat === 'All')) {
            cards[i].style.display = "";
        }
        else if (director.innerText.toUpperCase().indexOf(filter) > -1 && (cat === 'Director' || cat === 'All')) {
            cards[i].style.display = "";
        }
        else {
            cards[i].style.display = "none";
        }
    }

    $categories.isotope('layout');
}


// --- Add media to favorite -------------------------------------------
function addFavorite(element_id, media_type) {
    let favorite

    favorite = !!$('#fav-' + element_id).hasClass('far');

    $.ajax ({
        type: "POST",
        url: "/add_favorite",
        contentType: "application/json",
        data: JSON.stringify({ element_id: element_id, element_type: media_type, favorite: favorite }),
        dataType: "json",
        success: function() {
            if (favorite === true) {
                $('#fav-'+element_id).removeClass('far card-btn-bottom-left').addClass('fas card-favorite')
                $('#fav-'+element_id).attr('style', 'color: darkgoldenrod;')
            } else {
                $('#fav-'+element_id).removeClass('fas card-favorite').addClass('far card-btn-bottom-left')
                $('#fav-'+element_id).attr('style', 'color: white;')
            }
        },
        error: function() {
            error_ajax_message('Error trying to add the media to you favorite. Please try again later.')
        }
    });
}


// --- Show/Hide common media ------------------------------------------
function HideCommon() {
    if ($('#SharedMedia').prop("checked") === true) {
        $('.card-ribbon').parent().parent().parent().hide();
    }
    else if ($('#SharedMedia').prop("checked") === false && $('#ShowFavorites').prop("checked") === true) {
        $('.card-ribbon').parent().parent().parent().show();
        $('.far.fa-star').parent().parent().parent().hide();
    }
    else if ($('#SharedMedia').prop("checked") === false && $('#ShowFavorites').prop("checked") === false) {
        $('.card-ribbon').parent().parent().parent().show();
    }

    $categories.isotope('layout');
}


// --- Show/Hide favorites media ---------------------------------------
function ShowFavorites() {
    if ($('#ShowFavorites').prop("checked") === true) {
        $('.far.fa-star').parent().parent().parent().hide();
    }
    else if ($('#ShowFavorites').prop("checked") === false && $('#SharedMedia').prop("checked") === true) {
        $('.far.fa-star').parent().parent().parent().show();
        $('.card-ribbon').parent().parent().parent().hide();
    }
    else if ($('#ShowFavorites').prop("checked") === false && $('#SharedMedia').prop("checked") === false) {
        $('.far.fa-star').parent().parent().parent().show();
    }

    $categories.isotope('layout');
}


// --- Add the category to the user (from other list) ------------------
function AddCatUser(cat, card_id, media_id, media_type) {
    $.ajax ({
        type: "POST",
        url: "/add_element",
        contentType: "application/json",
        data: JSON.stringify({element_cat: cat.childNodes[0].data, element_id: media_id, element_type: media_type}),
        dataType: "json",
        success: function() {
            removeCat();
            $("#"+card_id).children().children('div[class="view overlay"]').append("<div class='card-ribbon'></div>");
            $("#"+card_id).children().children().children().remove(".card-btn-top-left.fas.fa-plus.text-light");
        },
        error: function () {
            error_ajax_message('Error trying to add the media. Please try again later.')
        }
    });
}


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
    let filterValue = $(this).attr('data-filter');
    $categories.isotope({ filter: filterValue });
});
$('.filters-button-group').each(function(i, buttonGroup) {
    let $buttonGroup = $(buttonGroup);
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
    let $window = $(window),
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
