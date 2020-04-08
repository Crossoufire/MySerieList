// -------------------- Tooltip and Datatable -----------------------------
$(document).ready(function () {
    // Datatable functions
    $('#all_history').DataTable({
        columnDefs: [
            {orderable: false, targets: 0},
            {orderable: true, targets: 1},
            {orderable: false, targets: 2},
            {orderable: false, targets: 3}
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
