// ------------- Change category --------------
function changeCategory(element_id, new_category, tr_id, mod_id, media_list) {
    if (new_category === 'Completed') {
        var plan_to_watch = 'Plan to Watch';

        $("#"+mod_id+ " a").filter(":contains('Completed')").remove()
        $("#"+mod_id+ " a").filter(":contains('Plan to Watch')").remove()

        $("#"+mod_id).prepend(
            "<a data-dismiss='modal' class='list-group-item text-light bg-dark modded' onclick='changeCategory(\"" + element_id + "\", \"" + plan_to_watch + "\", \"" + tr_id + "\", \"" + mod_id + "\", \"" + media_list + "\")'>Plan to Watch</a>"
        );
        $("#" + tr_id).prependTo("#tbody_COMPLETED");
        $('.modal').modal("hide");
    }

    if (new_category === 'Plan to Watch') {
        var completed = 'Completed';

        $("#"+mod_id+ " a").filter(":contains('Completed')").remove()
        $("#"+mod_id+ " a").filter(":contains('Plan to Watch')").remove()

        $("#"+mod_id).prepend(
            "<a data-dismiss='modal' class='list-group-item text-light bg-dark modded' onclick='changeCategory(\"" + element_id + "\", \"" + completed + "\", \"" + tr_id + "\", \"" + mod_id + "\", \"" + media_list + "\")'>Completed</a>"
        );
        $("#" + tr_id).prependTo("#tbody_PLAN_TO_WATCH");
        $('.modal').modal("hide");
    }

    $body = $("body");
    $grid.isotope('layout');
    $.ajax ({
        type: "POST",
        url: "/change_element_category",
        contentType: "application/json",
        data: JSON.stringify({status: new_category, element_id: element_id, element_type: media_list }),
        dataType: "json",
        success: function(response) {
            console.log("ok"); }
    });
}

// ------------- Delete element ---------------
function delete_element(element_id, tr_id, media_list) {
    if (!confirm("Are you sure you want to delete this element from your list?")){
        return false;
    }
    $("#"+tr_id).remove();
    $body = $("body");
    $.ajax ({
        type: "POST",
        url: "/delete_element",
        contentType: "application/json",
        data: JSON.stringify({delete: element_id, element_type: media_list }),
        dataType: "json",
        success: function(response) {
            console.log("ok"); }
    });
}


// --------------- Isotope categories ------------------
var $grid = $('.table-iso').isotope({
    itemSelector: '.category',
    layoutMode: 'masonry'
});

// bind filter button click
$('.filters-button-group').on('click', 'button', function() {
    var filterValue = $(this).attr('data-filter');
    console.log(filterValue);
    $grid.isotope({ filter: filterValue });
});

// change the class on the selected button
$('.filters-button-group').each(function(i, buttonGroup) {
    var $buttonGroup = $(buttonGroup);
    $buttonGroup.on('click', 'button', function() {
        $buttonGroup.find('.btn-warning').addClass('btn-light');
        $buttonGroup.find('.btn-warning').removeClass('btn-warning');
        $(this).addClass('btn-warning');
        $(this).removeClass('btn-light');
    });
});


 $grid.isotope('layout');