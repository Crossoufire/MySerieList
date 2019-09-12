
$(document).ready(function () {
    $('#hall_of_fame').DataTable({
        "order": [[ 5, "desc" ], [ 1, "asc" ]],
        columnDefs: [{orderable: false, targets: 0},
                     {orderable: false, targets: 6}],
    });
    $('.dataTables_length').addClass('bs-select');
});

function follow(follow_id) {
    $body = $("body");
    $.ajax ({
        type: "POST",
        url: "/follow",
        contentType: "application/json",
        data: JSON.stringify({follow: follow_id}),
        dataType: "json",
        beforeSend: function() { $body.addClass("loading"); },
        success: function(response) {
            window.location.replace('/hall_of_fame'); }
    });
}