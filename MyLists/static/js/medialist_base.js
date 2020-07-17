

// --- Delete element --------------------------------------------------
function deleteElement(card, media_list) {
    let element_id = $(card)[0].id.split('_')[1];
    let load_img = $(card).find('.view.overlay');
    load_img.prepend(Loading());

    if (!confirm('Delete the media from your list?')) {
        load_img.find('.load-medialist').remove();
        return false;
    }

    $.ajax ({
        type: "POST",
        url: "/delete_element",
        contentType: "application/json",
        data: JSON.stringify({ delete: element_id, element_type: media_list }),
        dataType: "json",
        success: function() {
            $(card).remove();
        },
        error: function () {
            error_ajax_message('Error trying to remove the media. Please try again later.')
        },
        complete: function () {
            load_img.find('.load-medialist').remove();
        }
    });

    $categories.isotope('layout');
}


// --- Remove the category buttons -------------------------------------
function removeCat() {
    $('.card-cat-buttons').remove();
    $('.card-btn-top-right').remove();
    $('.card-btn-toop-right').show();
    $('.card-btn-top-left').show();
    $('.bottom-card-info').show();

    $('.seas-eps-drop-container').each(function () {
        if ($(this).parent().parent().parent()[0].className === 'row category-PLAN TO WATCH' ||
            $(this).parent().parent().parent()[0].className === 'row category-RANDOM') {
            $(this).hide();
        }
        else {
            $(this).show();
        }
    });

    $('.card-img-top').attr('style', 'filter: brightness(100%); height: auto;');
    $('.mask').show();
}


// --- Search in medialist ---------------------------------------------
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
function addFavorite(fav_div, element_id, media_type) {
    let favorite = !!$(fav_div).hasClass('far');

    $.ajax ({
        type: "POST",
        url: "/add_favorite",
        contentType: "application/json",
        data: JSON.stringify({ element_id: element_id, element_type: media_type, favorite: favorite }),
        dataType: "json",
        success: function() {
            if (favorite === true) {
                $(fav_div).removeClass('far').addClass('fas favorited');
            } else {
                $(fav_div).removeClass('fas favorited').addClass('far');
            }
        },
        error: function() {
            error_ajax_message('Error trying to favorite the media. Please try again later.')
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
        $('.far.fa-star').parent().parent().parent().parent().parent().hide();
    }
    else if ($('#ShowFavorites').prop("checked") === false && $('#SharedMedia').prop("checked") === true) {
        $('.far.fa-star').parent().parent().parent().parent().parent().show();
        $('.card-ribbon').parent().parent().parent().parent().parent().hide();
    }
    else if ($('#ShowFavorites').prop("checked") === false && $('#SharedMedia').prop("checked") === false) {
        $('.far.fa-star').parent().parent().parent().parent().parent().show();
    }

    $categories.isotope('layout');
}


// --- Add the category to the user (from other list) ------------------
function AddCatUser(category, card_id) {
    let media_list = $('#'+card_id).attr('values').split('-')[1];
    let element_id = $('#'+card_id).attr('values').split('-')[2];
    let load_img = $('#'+card_id).find('.view.overlay');
    load_img.prepend(Loading());

    $.ajax ({
        type: "POST",
        url: "/add_element",
        contentType: "application/json",
        data: JSON.stringify({element_cat: category, element_id: element_id, element_type: media_list}),
        dataType: "json",
        success: function() {
            $("#"+card_id).find('.view.overlay').append('<div class="card-ribbon"></div>');
            $("#"+card_id).find('.card-btn-top-left').remove();
        },
        error: function () {
            error_ajax_message('Error trying to add the media to your list. Please try again later.')
        },
        complete: function () {
            removeCat();
            load_img.find('.load-medialist').remove();
        }
    });
}


// --- Show comments ---------------------------------------------------
function showComment(card, media_type, media_id, current_user) {
    let media_name = $(card).find('.font-mask').text();
    let comment = $("#com_"+media_id).text();

    if (current_user === true) {
        var edit_button = ('<a href="/comment/'+media_type+'/'+media_id+'">' +
            '<button class="btn btn-sm btn-primary">' +
                'Edit' +
            '</button>' +
            '</a>'
        )
    }

    $('body').append(
        '<div id="commentModal" class="modal" tabindex="-1" role="dialog">' +
            '<div class="modal-dialog modal-dialog-centered" role="document">' +
                '<div class="modal-content">' +
                    '<div class="modal-header">' +
                        '<h5 class="modal-title text-light"><b>'+media_name+'</b></h5>' +
                        '<button type="button" class="close text-light" onclick="removeModal()"' +
                            '<span aria-hidden="true">&times;</span>' +
                        '</button>' +
                    '</div>' +
                    '<div class="modal-body text-light">' +
                        '<p>'+comment+'</p>' +
                    '</div>' +
                    '<div class="modal-footer p-1">' +
                        edit_button +
                    '</div>' +
                '</div>' +
            '</div>' +
        '</div>'
    );

    $('#commentModal').modal({backdrop: 'static', keyboard: false});
}


// --- Remove comments modal -------------------------------------------
function removeModal() {
    $('#commentModal').remove();
    $('.modal-backdrop.show').remove();
}


// --- Create the score dropdown ---------------------------------------
function scoreDrop(score, data_id, media_list) {
    $(score).hide();
    let score_value = $(score).text();
    let drop = document.createElement("select");
    drop.className = "score-drop";
    drop.setAttribute('values', ''+data_id+','+media_list);
    let option = document.createElement("option");
    option.className = "seas-eps-drop-options";
    option.value = "---";
    option.text = "---";
    drop.appendChild(option);
    for (let i = 0; i <= 10; i+=0.5) {
        let option = document.createElement("option");
        option.className = "seas-eps-drop-options";
        option.value = ""+i;
        if (i === parseFloat(score_value)) {
            option.selected = true;
        }
        if (i < 10) {
            option.text = ""+i.toFixed(1);
        } else {
            option.text = ""+i;
        }
        drop.appendChild(option);
    }
    $(score).parent().prepend(drop);
    drop.focus();
}


// --- Change the score and delete dropdown ----------------------------
$(document).on('change focusout','.score-drop',function(event) {
    let value = parseFloat(this.value).toFixed(1);
    let media_id = $(this).attr('values').split(',')[0];
    let media_list = $(this).attr('values').split(',')[1];

    if (isNaN(value)) {
        value = "---";
    } else if (value === "10.0") {
        value = 10;
    }

    if (event.type === 'change') {
        $.ajax ({
            type: "POST",
            url: "/update_score",
            contentType: "application/json",
            data: JSON.stringify({score: value, element_id: media_id, element_type: media_list}),
            dataType: "json",
            success: function() {
                $('#score_'+media_id).text(value).show();
                $(this).remove();
            },
            error: function () {
                error_ajax_message('Error trying to change the media score. Please try again later.')
            }
        });
    }

    $('#score_'+media_id).text(value).show();
    this.remove();
});


// --- Create the rewatch dropdown -------------------------------------
function rewatchDrop(rewatch, data_id, media_list) {
    $(rewatch).hide();
    let rewatch_value = $(rewatch).text();
    let drop = document.createElement("select");
    drop.className = "rewatch-drop";
    drop.setAttribute('values', ''+data_id+','+media_list);
    let option = document.createElement("option");
    option.className = "seas-eps-drop-options";
    for (let i = 0; i < 11; i++) {
        let option = document.createElement("option");
        option.className = "seas-eps-drop-options";
        option.value = ""+i;
        if (i === parseInt(rewatch_value)) {
            option.selected = true;
        }
        option.text = ""+i;
        drop.appendChild(option);
    }
    $(rewatch).parent().prepend(drop);
    drop.focus();
}


// --- Change the rewatch and delete dropdown --------------------------
$(document).on('change focusout','.rewatch-drop',function(event) {
    let value = parseInt(this.value);
    let media_id = $(this).attr('values').split(',')[0];
    let media_list = $(this).attr('values').split(',')[1];

    if (event.type === 'change') {
        $.ajax ({
            type: "POST",
            url: "/update_rewatch",
            contentType: "application/json",
            data: JSON.stringify({rewatch: value, element_id: media_id, element_type: media_list}),
            dataType: "json",
            success: function() {
                $('#rew_'+media_id).text(value).show();
                $(this).remove();
            },
            error: function () {
                error_ajax_message('Error trying to change the rewatched value for the media. Please try again later.')
            }
        });
    }

    $('#rew_'+media_id).text(value).show();
    this.remove();
});


// --- Isotopes categories ---------------------------------------------
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
    $categories.isotope({
        filter: filterValue
    });
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


// --- Row gutters -----------------------------------------------------
$(document).ready(function() {
    function a() {
        if ($(window).width() < 1025) {
            return $('.row').addClass('no-gutters');
        }
        $('.row').removeClass('no-gutters');
    }

    $(window).resize(a).trigger('resize');
    $categories.isotope('layout');
});


// --- Create the loading screen on media ------------------------------
function Loading() {
    return ('<div class="load-medialist">' +
                '<img class="img-load-medialist" src="/static/img/loading.webp" alt="">' +
            '</div>')
}