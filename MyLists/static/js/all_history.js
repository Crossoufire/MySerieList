

// --- Datatable ----------------------------------------------------
$(document).ready(function () {
    // --- Datatable functions -----------------
    $('#all_history').DataTable({
        "bPaginate": false,
        "bLengthChange": false,
        "bFilter": false,
        "bInfo": false,
        "bAutoWidth": false,
        "searching": true,
        columnDefs: [
            {orderable: false, targets: 0},
            {orderable: true, targets: 1},
            {orderable: false, targets: 2},
            {orderable: true, targets: 3}
        ],
    });
    $('.dataTables_length').addClass('bs-select');
});
