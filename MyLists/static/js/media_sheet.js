

// --- Add the media to the user ---------------------------
function addToUser(element_id, media_type) {
    $('#your-medialist-data').show();
    $('#addlist').hide();
    $('#removeList').show();

    let category;

    if (media_type === 'movieslist') {
       category = 'Plan to Watch';
    } else {
       category = 'Watching';
    }

    $body = $("body");
    $.ajax ({
        type: "POST",
        url: "/add_element",
        contentType: "application/json",
        data: JSON.stringify({element_id: element_id, element_type: media_type, element_cat: category}),
        dataType: "json",
        success: function(response) {
            let info = response.data;
            if (info['code'] === 500) {
                $('.container > .content').append(
                    '<div class="alert alert-' + info['category'] + 'alert-dismissible m-t-15" role="alert">' +
                        '<button type="button" class="close" data-dismiss="alert" aria-label="Close">' +
                            '<span aria-hidden="true">&times;</span>' +
                        '</button>' +
                            info['body'] +
                    '</div>');
            }
        }
    });
}


// --- Remove the media to the user ------------------------
function removeFromUser(element_id, media_type) {
    $('#your-medialist-data').hide();
    $('#removeList').hide();
    $('#addlist').show();

    if (media_type !== 'movieslist') {
        $('#category-dropdown').val('Watching');
        $('#season-dropdown').val("0");
        $('#episode-dropdown').val("0");
    } else {
        $('#category-dropdown').val('Plan to Watch');
    }

    $body = $("body");
    $.ajax ({
        type: "POST",
        url: "/delete_element",
        contentType: "application/json",
        data: JSON.stringify({ delete: element_id, element_type: media_type }),
        dataType: "json",
        success: function(response) {
            console.log("ok");
        }
    });
}


// --- Set media to favorite -------------------------------
function addFavorite(element_id, media_type) {
    let favorite;

    if ($('#favorite').hasClass('far')) {
        $('#favorite').addClass('fas').removeClass('far');
        $('#alert').addClass('alert-success').removeClass('alert-warning');
        $('#alert').attr('style', 'display: block;');
        $('#alert').html('');
        $('#alert').html('<i class="fas fa-check m-r-5"></i> Added to favorite');
        $('#alert').delay(800).fadeOut('slow');
        favorite = true;
    }
    else {
        $('#favorite').addClass('far').removeClass('fas');
        $('#alert').addClass('alert-warning').removeClass('alert-success');
        $('#alert').attr('style', 'display: block;');
        $('#alert').html('');
        $('#alert').html('<i class="fas fa-times m-r-5"></i> Removed from favorite');
        $('#alert').delay(800).fadeOut('slow');
        favorite = false;
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


// --- Change the TV category ------------------------------
function changeCategoryTV(element_id, cat_selector, seas_data, media_list) {
    let new_cat = cat_selector.options[cat_selector.selectedIndex].value;

    $('#season-row').show();
    $('#episode-row').show();

    if (new_cat === 'Completed') {
        let season_data = JSON.parse("["+seas_data+"]");
        let episode_drop = document.getElementById('episode-dropdown');

        let seasons_length = $('#season-dropdown').children('option').length;
        let seasons_index = (seasons_length - 1);
        $('#season-dropdown').prop('selectedIndex', seasons_index);

        episode_drop.length = 1;

        for (i = 2; i <= season_data[0][seasons_index]; i++) {
            let opt = document.createElement("option");
            opt.className = "";
            if (i <= 9) {
                opt.text = i;
            } else {
                opt.text = i;
            }
            episode_drop.appendChild(opt);
        }
        $('#episode-dropdown').prop('selectedIndex', season_data[0][seasons_index]-1);
    }
    else if (new_cat === 'Random') {
        $('#season-row').hide();
        $('#episode-row').hide();
    }
    else if (new_cat === 'Plan to Watch') {
        $('#season-row').hide();
        $('#episode-row').hide();
    }

    $body = $("body");
    $.ajax ({
        type: "POST",
        url: "/change_element_category",
        contentType: "application/json",
        data: JSON.stringify({status: new_cat, element_id: element_id, element_type: media_list }),
        dataType: "json",
        success: function(response) {
            console.log("ok");
        }
    });
}


// --- Change the Movie category ---------------------------
function changeCategoryMovies(element_id, cat_selector, genres) {
    let new_cat = cat_selector.options[cat_selector.selectedIndex].value;

    if (new_cat === 'Completed') {
        if (genres.includes("Animation")) {
           new_cat = 'Completed Animation';
        }
    }

    $body = $("body");
    $.ajax ({
        type: "POST",
        url: "/change_element_category",
        contentType: "application/json",
        data: JSON.stringify({status: new_cat, element_id: element_id, element_type: 'movieslist' }),
        dataType: "json",
        success: function(response) {
            console.log("ok");
        }
    });
}


// --- Update season ---------------------------------------
function updateSeason(element_id, value, seas_data, media_list) {
    let selected_season = value.selectedIndex;
    let episode_drop = document.getElementById('episode-dropdown');
    let season_data = JSON.parse("["+seas_data+"]");

    console.log(selected_season)

    episode_drop.length = 1;
    for (i = 2; i <= season_data[0][selected_season]; i++) {
        let opt = document.createElement("option");
        opt.className = "";
        if (i <= 9) {
                opt.text = i;
            } else {
                opt.text = i;
            }
        episode_drop.appendChild(opt);
    }

    $body = $("body");
    $.ajax ({
        type: "POST",
        url: "/update_element_season",
        contentType: "application/json",
        data: JSON.stringify({season: selected_season, element_id: element_id, element_type: media_list }),
        dataType: "json",
        success: function(response) {
            console.log("ok"); }
    });
}


// --- Update episode --------------------------------------
function updateEpisode(element_id, episode, media_list) {
    let selected_episode = episode.selectedIndex;

    $body = $("body");
    $.ajax ({
        type: "POST",
        url: "/update_element_episode",
        contentType: "application/json",
        data: JSON.stringify({episode: selected_episode, element_id: element_id, element_type: media_list }),
        dataType: "json",
        success: function(response) {
            console.log("ok"); }
    });
}


// --- Lock the media --------------------------------------
function lock_media(element_id, element_type) {
    let lock_status;

    if ($('#lock-button').prop("checked") === true) {
        $('#lock-button-label').text('Media is Locked')
        $('#edit-button').attr('style', 'display: "";');
        lock_status = true;
    } else {
        $('#lock-button-label').text('Media is Unlocked');
        $('#edit-button').attr('style', 'display: none;');
        lock_status = false;
    }

    $body = $("body");
    $.ajax ({
        type: "POST",
        url: "/lock_media",
        contentType: "application/json",
        data: JSON.stringify({element_id: element_id, element_type: element_type, lock_status: lock_status }),
        dataType: "json",
        success: function(response) {
            console.log("ok"); }
    });
}


// --- Tooltip ---------------------------------------------
$(document).ready(function() {
    // Tooltip initialization
    $(function () {
        $('[data-toggle="tooltip"]').tooltip()
    })
});


// --- Random box color ------------------------------------
let colors = ['#6e7f80', '#536872', '#708090', '#536878', '#36454f'];
let boxes = document.querySelectorAll(".box");

for (i = 0; i < boxes.length; i++) {
    boxes[i].style.backgroundColor = colors[Math.floor(Math.random()*colors.length)];
}
