

// ------------------------ Follow status ---------------------------------
function follow_status(follow_id, button) {
    let status;

    if ($(button)[0].innerText === 'UNFOLLOW') {
        $(button).text('Follow');
        $(button).addClass('btn-primary').removeClass('btn-dark btn-smaller');
        status = false;
    } else {
        $(button).text('Unfollow');
        $(button).removeClass('btn-primary').addClass('btn-dark btn-smaller');
        status = true;
    }

    $.ajax ({
        type: "POST",
        url: "/follow_status",
        contentType: "application/json",
        data: JSON.stringify({follow_id: follow_id, follow_status: status}),
        dataType: "json",
        success: function() {
            console.log("ok"); }
    });
}


// -------------------- Tooltip and Datatable -----------------------------
$(document).ready(function () {
    // --- Hall of Fame datatable functions ------------------
    $('#hall_of_fame').DataTable({
        "order": [[ 0, "desc" ]],
        columnDefs: [
            {orderable: true, targets: 0},
            {orderable: false, targets: 5}
        ],
        "lengthMenu": [[25, 50, 100, -1], [25, 50, 100, "All"]],
    });
    $('.dataTables_length').addClass('bs-select');


    // --- More stats datatable functions --------------------
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

    // Tooltip init
    $('.tooltip').tooltip();
    $(function () {
        $('[data-toggle="tooltip"]').tooltip()
    })
});
