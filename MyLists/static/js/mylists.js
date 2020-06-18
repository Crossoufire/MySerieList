

// --- Autocomplete ---------------------------------------------------------
$.widget("custom.catcomplete", $.ui.autocomplete, {
    _create: function() {
        this._super();
        this.widget().menu("option", "items", "> :not(.ui-autocomplete-category)");
    },
    _renderMenu: function(ul, items) {
        let that = this,
            currentCategory = "";
        ul.attr('style', 'padding-top: 9px;');
        $.each(items, function(index, item) {
            let li;
            if (item.nb_results === 0) {
                let a = "No results found."
                ul.append('<li class="disabled bg-dark text-light">' + a + '</li>');
            } else {
                li = that._renderItemData(ul, item);
            }
        });
    },
    _renderItem: function(ul, item) {
        let $li = $('<li class="bg-dark p-t-2 p-b-2" style="border-bottom: solid black 1px;">');

        $li.append(
            "<div class='row'>" +
            "<div class='col' style='min-width: 60px; max-width: 60px;'>" +
            "<img src="+item.poster_path+" alt="+item.name+" style='width: 50px; height: 75px;'>" +
            "</div>" +
            "<div class='col'>" +
            "<a class='text-light'>" +
            " "+item.name+" " +
            "<br>" +
            "<span style='font-size: 10pt;'>("+item.first_air_date+")</span>" +
            "</a>" +
            "</div>" +
            "</div>");

        return $li.appendTo(ul);
    }
});


// --- Autocomplete ---------------------------------------------------------
$(function() {
    $("#autocomplete").catcomplete({
        delay: 200,
        source: function(request, response) {
            $.getJSON("/autocomplete", {
                    q: request.term,
                },
                function(data) {
                    response(data.matching_results);
                }
            );
        },
        minLength: 2,
        select: function(event, ui) {
            var form = document.createElement("form");
            form.method = "POST";
            form.action = "/check_media/"+ui.item.media_type+"/"+ui.item.tmdb_id;
            document.body.appendChild(form);
            form.submit();
        }
    });
});


// --- AJAX Notification ----------------------------------------------------
$('#ajax-notif').click(function a () {
    $('.notif-badge').attr('style', 'background-color: grey;');
    $('.notif-badge').html(0);

    $(".notif-item-container").remove();
    $('#loading-image').show();

    $.ajax ({
        type: "GET",
        url: "/read_notifications",
        contentType: "application/json",
        dataType: "json",
        success: function(data) {
            display_notifications(data);
        },
        complete: function() {
            $('#loading-image').hide();
        }
    });
});


// --- Notification ---------------------------------------------------------
function display_notifications(data) {
    let resp = data.results;
    if (resp.length === 0) {
        $("#notification-items").append('<div class="notif-item-container p-2">' +
            '<i>You do not have notifications for now.</i>' +
            '</div>');
    }
    else {
        for (let i = 0; i < resp.length; i++) {
            if (resp[i]['media_type'] === 'movieslist') {
                $("#notification-items").append(
                    '<div class="notif-item-container p-2">' +
                    '<i class="fas fa-film" style="color: #8c7821;"></i>' +
                    '&nbsp;&nbsp;' +
                    '<a style="color: #359aff;" href="/media_sheet/Movies/'+resp[i]['media_id']+'">' +
                    resp[i]['name'] + '</a>' +
                    '<i class="fas fa-arrow-right"></i>' +
                    '&nbsp;&nbsp;Airs the ' + resp[i]['release_date'] +
                    '&nbsp;&nbsp;&nbsp;&nbsp;' +
                    '</div>');
            }
            else if (resp[i]['media_type'] === 'serieslist') {
                $("#notification-items").append(
                    '<div class="notif-item-container p-2">' +
                    '<i class="fas fa-tv" style="color: #216e7d;"></i>' +
                    '&nbsp;&nbsp;' +
                    '<a style="color: #359aff;" href="/media_sheet/Series/'+resp[i]['media_id']+'">' +
                    resp[i]['name'] + '</a>' +
                    'S0' + resp[i]['season']+'.E0'+resp[i]['episode'] +
                    ' <i class="fas fa-arrow-right"></i>' +
                    '&nbsp;&nbsp;Airs the ' + resp[i]['release_date'] +
                    '&nbsp;&nbsp;&nbsp;&nbsp;' +
                    '</div>');
            }
            else {
                $("#notification-items").append(
                    '<div class="notif-item-container p-2">' +
                    '<i class="fas fa-torii-gate" style="color: #945141;"></i>' +
                    '&nbsp;&nbsp;' +
                    '<a style="color: #359aff;" href="/media_sheet/Anime/'+resp[i]['media_id']+'">' +
                    resp[i]['name'] + '</a>' +
                    'S0' + resp[i]['season']+'.E0'+resp[i]['episode'] +
                    ' <i class="fas fa-arrow-right"></i>' +
                    '&nbsp;&nbsp;Airs the ' + resp[i]['release_date'] +
                    '&nbsp;&nbsp;&nbsp;&nbsp;' +
                    '</div>');
            }
        }
    }
}


// --- Tooltip initialization -----------------------------------------------
$(function () {
    $('[data-toggle="tooltip"]').tooltip()
});


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
