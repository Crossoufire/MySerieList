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

// ----------- Turn the arrow ---------------
function turn(category, arrow) {
    var arrow = document.getElementById(arrow);
    var category = document.getElementById(category);

    if (category.className === "d-flex flex-wrap table-responsive-sm collapsing") {
    } else if (arrow.className === "collapse_all fas fa-sm fa-chevron-right") {
        arrow.className = "collapse_all fas fa-sm fa-chevron-down";
    } else {
        arrow.className = "collapse_all fas fa-sm fa-chevron-right";
    }
}