

// --- Datatable -----------------------------------------------------------------------------------
$(document).ready(function () {
    $('#hall_of_fame').DataTable({
        "order": [[ 0, "desc" ]],
        "lengthMenu": [[25, 50, 100, -1], [25, 50, 100, "All"]],
    });

    $('#imported').DataTable({
        "order": [[ 0, "desc" ]],
        columnDefs: [
<<<<<<< HEAD
            {orderable: false, targets: 0},
            {orderable: true, targets: 1},
            {orderable: true, targets: 2}
=======
            {orderable: true, targets: 0},
            {orderable: false, targets: 5}
>>>>>>> parent of 21634e6 (testing games)
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


