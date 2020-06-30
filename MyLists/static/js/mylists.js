

// --- Autocomplete ---------------------------------------------------------
$(function() {
    $("#autocomplete").catcomplete({
        delay: 200,
        minLength: 2,
        source: function(request, response) {
            $.getJSON("/autocomplete", {
                q: request.term,
            },
            function(data) {
                response(data.search_results);
            });
        },
        select: function(event, ui) {
            let form = document.createElement("form");
            form.method = "POST";
            form.action = "/media_sheet/"+ui.item.media_type+"/"+ui.item.tmdb_id+"?search=True";
            document.body.appendChild(form);
            form.submit();
        }
    });
});

$.widget("custom.catcomplete", $.ui.autocomplete, {
    "_renderItem": function(ul, item) {
        ul.addClass('autocomplete-ul');

        let media, $li;

        if (item.media_type === "serieslist") {
            media = 'TV Show';
            item.media_type = 'Series';

        } else if (item.media_type === "animelist") {
            media = 'Anime';
            item.media_type = 'Anime';
        } else {
            media = 'Movie';
            item.media_type = 'Movies';
        }

        if (item.nb_results === 0) {
            let a = "No results found.";
            $li = $('<li class="disabled bg-dark text-light p-l-5">'+ a + '</li>');
        } else {
            $li = $('<li class="bg-dark p-t-2 p-b-2" style="border-bottom: solid black 1px;">');

            $li.append(
                '<div class="row">' +
                    '<div class="col" style="min-width: 60px; max-width: 60px;">' +
                        '<img src="'+item.poster_path+'" alt="'+item.name+'" style="width: 50px; height: 75px;">' +
                    '</div>' +
                    '<div class="col">' +
                        '<a class="text-light">' + item.name +
                            '<br>' +
                            '<span style="font-size: 10pt;">' + media + ' | ' + item.first_air_date + '</span>' +
                        '</a>' +
                    '</div>' +
                '</div>');
        }
        return $li.appendTo(ul);
    }
});


// --- Notification ---------------------------------------------------------
function display_notifications(data) {
    let add_hr;
    let resp = data.results;
    if (resp.length === 0) {
        $("#notif-dropdown").append(
            '<a class="dropdown-item notif-items text-light">' +
                '<i>You do not have notifications for now.</i>' +
            '</a>'
        );
    }
    else {
        for (let i = 0; i < resp.length; i++) {
            // Add the time and date for the follow
            let tz = new Intl.DateTimeFormat().resolvedOptions().timeZone;
            let localdate = new Date(resp[i]['timestamp']).toLocaleString("en-GB", {timeZone: tz});
            let d = new Date(resp[i]['timestamp'])
            let month = ["Jan", "Feb", "Mar", "Apr", "May", "Jun", "Jul", "Aug", "Sep", "Oct", "Nov", "Dec"];
            let timestamp = localdate.slice(0, 2) + " " + month[d.getMonth()] + " at " + localdate.slice(11, 17)

            // Add H-line between notifications except for the last one
            if (i + 1 === resp.length) {
                add_hr = '';
            } else {
                add_hr = '<hr class="p-0 m-t-0 m-b-0 m-l-15 m-r-15">';
            }

            if (resp[i]['media_type'] === 'serieslist') {
                $("#notif-dropdown").append(
                    '<a class="dropdown-item notif-items text-light" href="/media_sheet/Series/' +
                     resp[i]['media_id']+'">' +
                        '<div class="row no-gutters">' +
                            '<div class="col-2">' +
                                '<i class="fas fa-tv text-series"></i>' +
                            '</div>' +
                            '<div class="col-10 ellipsis-notif">' +
                                '<span><b>' + resp[i]['payload']['name'] + '</b></span>' +
                                '<div class="fs-14" style="color: darkgrey;">S0' + resp[i]['payload']['season'] + '.E0' +
                                resp[i]['payload']['episode'] + ' will begin on ' + resp[i]['payload']['release_date'] + '</div>' +
                            '</div>' +
                        '</div>' +
                    '</a>' +
                    '<div class="notif-items">' + add_hr + '</div>'
                );
            }
            else if (resp[i]['media_type'] === 'animelist') {
                $("#notif-dropdown").append(
                    '<a class="dropdown-item notif-items text-light" href="/media_sheet/Anime/' +
                    resp[i]['media_id']+'">' +
                        '<div class="row no-gutters">' +
                            '<div class="col-2">' +
                                '<i class="fas fa-torii-gate text-anime"></i>' +
                            '</div>' +
                            '<div class="col-10 ellipsis-notif">' +
                                '<span><b>' + resp[i]['payload']['name'] + '</b></span>' +
                                '<div class="fs-14" style="color: darkgrey;">S0' + resp[i]['payload']['season'] + '.E0' +
                                resp[i]['payload']['episode'] + ' will begin on ' + resp[i]['payload']['release_date'] + '</div>' +
                            '</div>' +
                        '</div>' +
                    '</a>' +
                    '<div class="notif-items">' + add_hr + '</div>'
                );
            }
            else if (resp[i]['media_type'] === 'movieslist') {
                $("#notif-dropdown").append(
                    '<a class="dropdown-item notif-items text-light" href="/media_sheet/Movies/' +
                    resp[i]['media_id']+'">' +
                        '<div class="row no-gutters">' +
                            '<div class="col-2">' +
                                '<i class="fas fa-film text-movies"></i>' +
                            '</div>' +
                            '<div class="col-10 ellipsis-notif">' +
                                '<span><b>' + resp[i]['payload']['name'] + '</b></span>' +
                                '<div class="fs-14" style="color: darkgrey;">Will be available on ' +
                                resp[i]['payload']['release_date'] + '</div>' +
                            '</div>' +
                        '</div>' +
                    '</a>' +
                    '<div class="notif-items">' + add_hr + '</div>'
                );
            }
            else {
                $("#notif-dropdown").append(
                    '<a class="dropdown-item notif-items text-light" href="/account/' +
                    resp[i]['payload']['username']+'">' +
                        '<div class="row no-gutters">' +
                            '<div class="col-2">' +
                                '<i class="fas fa-user" style="color: #45B29D;"></i>' +
                            '</div>' +
                            '<div class="col-10 ellipsis-notif">' +
                                '<span><b>' + resp[i]['payload']['message'] + '</b></span>' +
                                '<div class="fs-14" style="color: darkgrey;">' +
                                    timestamp +
                                '</div>' +
                            '</div>' +
                        '</div>' +
                    '</a>' +
                    '<div class="notif-items">' + add_hr + '</div>'
                );
            }
        }
    }
}


// --- Ajax error handling --------------------------------------------------
function error_ajax_message(message) {
    $('.content-message').prepend(
        '<div class="alert alert-danger alert-dismissible m-t-15">' +
            '<button type="button" class="close" data-dismiss="alert" aria-label="Close">' +
                '<span aria-hidden="true">&times;</span>' +
            '</button>' +
            message +
        '</div>');
}


// --- AJAX Notification ----------------------------------------------------
function notifications() {
    $('.notif-items').remove();
    $('#loading-image').show();

    $.ajax ({
        type: "GET",
        url: "/read_notifications",
        contentType: "application/json",
        dataType: "json",
        success: function(data) {
            $("#notif-badge").removeClass('badge-danger').addClass('badge-light').text(0);
            display_notifications(data);
        },
        error: function() {
            error_ajax_message('Error trying to recover the notifications. Please try again later.')
        },
        complete: function() {
            $('#loading-image').hide();
        }
    });
}


// --- Tooltip initialization -----------------------------------------------
$(function () {
    $('[data-toggle="tooltip"]').tooltip()
});


// --- Left dropdown for notifictaions on mobile  ---------------------------
$(document).ready(function() {
    function a() {
        if ($(window).width() < 991) {
            $('#profile-dropdown').removeClass('dropdown-menu-right');
            return $('#notif-dropdown').removeClass('dropdown-menu-right');
        }
        $('#profile-dropdown').addClass('dropdown-menu-right');
        $('#notif-dropdown').addClass('dropdown-menu-right');
    }

    $(window).resize(a).trigger('resize');
});
