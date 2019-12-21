
$(document).ready(function () {
    $('#hall_of_fame').DataTable({
        "order": [[ 5, "desc" ], [ 1, "asc" ]],
        columnDefs: [
            {orderable: false, targets: 0},
            {orderable: false, targets: 6}
        ],
        "lengthMenu": [[25, 50, 100, -1], [25, 50, 100, "All"]],
    });
    $('.dataTables_length').addClass('bs-select');
});

function follow(follow_id, button_id) {
    $('#'+button_id).text('Unfollow');
    $('#'+button_id).attr('onclick', "unfollow(\"" + follow_id + "\", \"" + button_id + "\")");
    $('#'+button_id).addClass('btn-dark');
    $('#'+button_id).removeClass('btn-primary');

    $.ajax ({
        type: "POST",
        url: "/follow",
        contentType: "application/json",
        data: JSON.stringify({follow: follow_id}),
        dataType: "json",
        success: function(response) {
            console.log("ok"); }
    });
}


function unfollow(follow_id, button_id) {
    $('#'+button_id).text('Follow');
    $('#'+button_id).attr('onclick', "follow(\"" + follow_id + "\", \"" + button_id + "\")");
    $('#'+button_id).addClass('btn-primary');
    $('#'+button_id).removeClass('btn-dark');

    $body = $("body");
    $.ajax ({
        type: "POST",
        url: "/unfollow",
        contentType: "application/json",
        data: JSON.stringify({unfollow: follow_id}),
        dataType: "json",
        success: function(response) {
            console.log("ok"); }
    });
}


// ------------------------------- Tooltip ----------------------------------
$('.tooltip').tooltip();
$(function () {
    $('[data-toggle="tooltip"]').tooltip()
})