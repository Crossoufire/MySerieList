

// --- Follow status -----------------------------------------------
function follow_status(follow_id, button) {
    let status;

    status = $(button)[0].innerText !== 'UNFOLLOW';

    $.ajax ({
        type: "POST",
        url: "/follow_status",
        contentType: "application/json",
        data: JSON.stringify({follow_id: follow_id, follow_status: status}),
        dataType: "json",
        success: function() {
            if ($(button)[0].innerText === 'UNFOLLOW') {
                $(button).text('Follow');
                $(button).addClass('btn-primary').removeClass('btn-dark btn-smaller');
            } else {
                $(button).text('Unfollow');
                $(button).removeClass('btn-primary').addClass('btn-dark btn-smaller');
            }
        },
        error: function () {
            error_ajax_message('Error updating the following status. Please try again later.');
        }
    });
}


// --- Datatable ---------------------------------------------------
$(document).ready(function () {
    $('#hall_of_fame').DataTable({
        "order": [[ 0, "desc" ]],
        columnDefs: [
            {orderable: true, targets: 0},
            {orderable: false, targets: 5}
        ],
        "lengthMenu": [[25, 50, 100, -1], [25, 50, 100, "All"]],
    });

    $('#more_stats').DataTable({
        "bFilter": false,
        "bInfo": false,
        "lengthChange": false,
        "bPaginate": false,
        "order": [[ 1, "desc" ]],
        columnDefs: [
            {orderable: true, targets: 0},
            {orderable: true, targets: 1},
            {orderable: true, targets: 2}
        ],
        "lengthMenu": [[-1], ["All"]],
    });

    $('.dataTables_length').addClass('bs-select');
});
