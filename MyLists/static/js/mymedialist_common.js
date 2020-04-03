
// ----------------------------- Delete element -----------------------------
function delete_element(element_id, card_id, media_list) {
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

// ---------------------- Remove the category list --------------------------
function remove_cat() {
    $('.card-cat-buttons').remove();
    $('.card-btn-top-right-2').remove();
    $('.card-btn-top-left').attr('style', 'display: block;');
    $('.card-btn-top-right').attr('style', 'display: block;');

    $('.seas-eps-box').each(function () {
        if ($(this).parent().parent().parent()[0].className == 'row category-PLAN TO WATCH') {
            $(this).attr('style', 'display: none;');
        } else {
            $(this).attr('style', 'display: inline-block;');
        }
    });

    $('.card-img-top').attr('style', 'filter: brightness(100%); height: auto;');
    $('.mask').show();
}

// ----------------------- Search by Title or Actor -------------------------
function searchElement() {
    var input, cat, filter, cards, cardContainer, title, i, l;
    input = document.getElementById("searchInput");
    cat = document.getElementsByClassName("search-select")[0].value;
    console.log(cat);
    filter = input.value.toUpperCase();
    cardContainer = document.getElementById("categories-iso");
    cards = cardContainer.getElementsByClassName("col-xl-2 col-lg-2 col-md-3 col-sm-3 col-4");
    l = cards.length;
    for (i = 0; i < l; i++) {
        title = cards[i].querySelector(".font-mask");
        original_title = cards[i].querySelector(".original-title");
        actors = cards[i].querySelector(".actors-yes");
        genres = cards[i].querySelector(".genre-yes");
        if (title.innerText.toUpperCase().indexOf(filter) > -1 && (cat == 'Title' || cat == 'All')) {
            cards[i].style.display = "";
        } else if (original_title.innerText.toUpperCase().indexOf(filter) > -1 && (cat == 'Title' || cat == 'All')) {
            cards[i].style.display = "";
        } else if (actors.innerText.toUpperCase().indexOf(filter) > -1 && (cat == 'Actors' || cat == 'All')) {
            cards[i].style.display = "";
        } else if (genres.innerText.toUpperCase().indexOf(filter) > -1 && (cat == 'Genres' || cat == 'All')) {
            cards[i].style.display = "";
        } else {
            cards[i].style.display = "none";
        }
    }

    $categories.isotope('layout');
}

// ------------------------- Select box & tooltip ---------------------------
$(document).ready(function() {
    // ---------- Select box ----------
    $('.add_element').val('');
    $('.cat-select').prop('selectedIndex', 0);

    // ----------- Tooltip ------------
    $('.tooltip').tooltip();
    $(function () {
        $('[data-toggle="tooltip"]').tooltip()
    })
});

// ------------------------- Isotopes ------------------------------------
var $categories = $('.categories-iso').isotope({
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
        $buttonGroup.find('.btn-warning').addClass('btn-light');
        $buttonGroup.find('.btn-warning').removeClass('btn-warning');
        $(this).addClass('btn-warning');
        $(this).removeClass('btn-light');
    });
});
$categories.isotope('layout');

// -------------------------- Row gutters --------------------------------
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