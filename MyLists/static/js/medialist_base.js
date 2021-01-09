

// --- Delete element --------------------------------------
function deleteElement(card, media_list) {
    let element_id = $(card)[0].id.split('_')[1];
    let $load_img = $(card).find('.view.overlay');

    $load_img.prepend(Loading());
    if (!confirm("Do you want to delete the media from your list?")) {
        $load_img.find('.load-medialist').remove();
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
        error: function() {
            error_ajax_message('Error trying to remove the media. Please try again later.')
        },
        complete: function() {
            $load_img.find('.load-medialist').remove();
        }
    });
}


// --- Remove the category buttons -------------------------
function removeCat() {
    $('.card-cat-buttons').remove();
    $('.card-btn-top-right').remove();
    $('.card-btn-toop-right').show();
    $('.bottom-card-cat').show();
    $('.bottom-card-cat-movie').show();
    $('.card-btn-top-left').show();
    $('.bottom-card-info').show();
    $('.mask').show();
    $('.card-img-top').attr('style', 'filter: brightness(100%); height: auto;');
}


// --- Add media to favorite -------------------------------
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
            error_ajax_message('Error trying to add the media to your favorite. Please try again later.')
        }
    });
}


// --- Add the category to the user (from other list) ------
function AddCatUser(category, card_id) {
    let $card = $('#'+card_id);
    let media_list = $card.attr('values').split('-')[1];
    let element_id = $card.attr('values').split('-')[2];
    let $load_img = $card.find('.view.overlay');

    $load_img.prepend(Loading());
    $.ajax ({
        type: "POST",
        url: "/add_element",
        contentType: "application/json",
        data: JSON.stringify({element_cat: category, element_id: element_id, element_type: media_list}),
        dataType: "json",
        success: function() {
            $card.find('.view.overlay').append('<div class="card-ribbon"></div>');
            $card.find('.card-btn-top-left').remove();
        },
        error: function() {
            error_ajax_message('Error trying to add the media to your list. Please try again later.')
        },
        complete: function() {
            removeCat();
            $load_img.find('.load-medialist').remove();
        }
    });
}


// --- Show comments ---------------------------------------
function showComment(card, media_type, media_id, current_user) {
    let media_name = $(card).find('.font-mask').text();
    let comment = $("#com_"+media_id).text();
    let edit_button = "";

    if (current_user === true) {
        edit_button = (
            '<div class="modal-footer p-1">' +
                '<a href="/comment/'+media_type+'/'+media_id+'">' +
                    '<button class="btn btn-sm btn-primary">' +
                        'Edit' +
                    '</button>' +
                '</a>' +
            '</div>'
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
                        edit_button +
                '</div>' +
            '</div>' +
        '</div>'
    );

    $('#commentModal').modal({backdrop: 'static', keyboard: false});
}


// --- Remove comments modal -------------------------------
function removeModal() {
    $('#commentModal').remove();
    $('.modal-backdrop.show').remove();
}


// --- Create the loading image on media -------------------
function Loading() {
    return ('<div class="load-medialist">' +
                '<div class="central-loading fas fa-3x fa-spinner fast-spin"></div>' +
            '</div>')
}


// --- Create the score dropdown ---------------------------
function scoreDrop(score, data_id, media_list) {
    let score_value = $(score).text();
    let drop = document.createElement("select");
    let option = document.createElement("option");
    let i;

    $(score).hide();

    drop.className = "score-drop";
    drop.setAttribute('values', ''+data_id+','+media_list);
    option.className = "seas-eps-drop-options";
    option.value = "---";
    option.text = "---";
    drop.appendChild(option);

    for (i = 0; i <= 10; i += 0.50) {
        let option = document.createElement("option");
        option.className = "seas-eps-drop-options";
        option.value = "" + i;
        if (i === parseFloat(score_value)) {
            option.selected = true;
        }
        if (i < 10) {
            option.text = "" + i.toFixed(1);
        } else {
            option.text = "" + i;
        }
        drop.appendChild(option);
    }

    $(score).parent().prepend(drop);
    drop.focus();
}


// --- Change/delete the score dropdown --------------------
$(document).on('change focusout','.score-drop',function(event) {
    let value = parseFloat(this.value).toFixed(1);
    let media_id = $(this).attr('values').split(',')[0];
    let media_list = $(this).attr('values').split(',')[1];
    let $score_id = $('#score_'+media_id);

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
                $score_id.text(value).show();
                $(this).remove();
            },
            error: function () {
                error_ajax_message('Error trying to change the media score. Please try again later.')
            }
        });
    }

    $score_id.text(value).show();
    this.remove();
});


// --- Create the rewatch dropdown -------------------------
function rewatchDrop(rewatch, data_id, media_list) {
    let rewatch_value = $(rewatch).text();
    let drop = document.createElement("select");
    let option = document.createElement("option");
    let i;

    $(rewatch).hide();

    drop.className = "rewatch-drop";
    drop.setAttribute('values', ''+data_id+','+media_list);
    option.className = "seas-eps-drop-options";

    for (i = 0; i < 11; i++) {
        let option = document.createElement("option");
        option.className = "seas-eps-drop-options";
        option.value = "" + i;
        if (i === parseInt(rewatch_value)) {
            option.selected = true;
        }
        option.text = "" + i;
        drop.appendChild(option);
    }

    $(rewatch).parent().prepend(drop);
    drop.focus();
}


// --- Change/delete the rewatch dropdown ------------------
$(document).on('change focusout', '.rewatch-drop', function(event) {
    let value = parseInt(this.value);
    let media_id = $(this).attr('values').split(',')[0];
    let media_list = $(this).attr('values').split(',')[1];
    let $rew_div = $('#rew_'+media_id);

    if (event.type === 'change') {
        $.ajax ({
            type: "POST",
            url: "/update_rewatch",
            contentType: "application/json",
            data: JSON.stringify({rewatch: value, element_id: media_id, element_type: media_list}),
            dataType: "json",
            success: function() {
                $rew_div.text(value).show();
                $(this).remove();
            },
            error: function () {
                error_ajax_message('Error trying to change the media rewatched value. Please try again later.')
            }
        });
    }

    $rew_div.text(value).show();
    this.remove();
});


// --- Create Row gutters ----------------------------------
$(document).ready(function() {
    let $row = $('.row');

    function gutter() {
        if ($(window).width() < 1025) {
            return $row.addClass('no-gutters');
        }
        $row.removeClass('no-gutters');
    }
    $(window).resize(gutter).trigger('resize');
});


// --- Init Infinite Scroll --------------------------------
$infini_scroll = $('.infinite-scroll-container');
$infini_scroll.infiniteScroll({
    path: '.pagination__next',
    append: '.card-container',
    status: '.scroller-status',
    hideNav: '.pagination.end',
});
