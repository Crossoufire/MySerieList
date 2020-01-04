

// ------------------------ Follow status ---------------------------------
function follow_status(follow_id, button) {
    var status;

    if ($(button).text() == 'Unfollow') {
        $(button).text('Follow');
        $(button).addClass('btn-primary').removeClass('btn-dark');
        status = false;
    } else {
        $(button).text('Unfollow');
        $(button).removeClass('btn-primary').addClass('btn-dark');
        status = true;
    }

    $body = $("body");
    $.ajax ({
        type: "POST",
        url: "/follow_status",
        contentType: "application/json",
        data: JSON.stringify({follow_id: follow_id, follow_status: status}),
        dataType: "json",
        success: function(response) {
            console.log("ok"); }
    });
}


// -------------------- Tooltip and Datatable -----------------------------
$(document).ready(function () {
    // Datables functions
    $('#hall_of_fame').DataTable({
        "order": [[ 5, "desc" ], [ 1, "asc" ]],
        columnDefs: [
            {orderable: false, targets: 0},
            {orderable: false, targets: 6}
        ],
        "lengthMenu": [[25, 50, 100, -1], [25, 50, 100, "All"]],
    });
    $('.dataTables_length').addClass('bs-select');

    // Tooltip init
    $('.tooltip').tooltip();
    $(function () {
        $('[data-toggle="tooltip"]').tooltip()
    })
});

