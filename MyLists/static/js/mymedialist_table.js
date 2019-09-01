// ------------- Change category --------------
function changeCategory(element_id, new_category, tr_id, mod_id, seas_drop_id, ep_drop_id, seas_data, media_list) {
    if (new_category === 'Watching') {
        var completed = 'Completed';
        var on_hold = 'On Hold';
        var random = 'Random';
        var dropped = 'Dropped';
        var plan_to_watch = 'Plan to Watch';

        $("#"+mod_id+ " a").filter(":contains('Watching')").remove()
        $("#"+mod_id+ " a").filter(":contains('Completed')").remove()
        $("#"+mod_id+ " a").filter(":contains('On Hold')").remove()
        $("#"+mod_id+ " a").filter(":contains('Random')").remove()
        $("#"+mod_id+ " a").filter(":contains('Dropped')").remove()
        $("#"+mod_id+ " a").filter(":contains('Plan to Watch')").remove()

        $("#"+mod_id).prepend(
            "<a data-dismiss='modal' class='list-group-item text-light bg-dark modded' onclick='changeCategory(\"" + element_id + "\", \"" + completed + "\", \"" + tr_id + "\", \"" + mod_id + "\", \"" + seas_drop_id + "\", \"" + ep_drop_id + "\", \"" + seas_data + "\", \"" + media_list + "\")'>Completed</a>" +
            "<a data-dismiss='modal' class='list-group-item text-light bg-dark modded' onclick='changeCategory(\"" + element_id + "\", \"" + on_hold + "\", \"" + tr_id + "\", \"" + mod_id + "\", \"" + seas_drop_id + "\", \"" + ep_drop_id + "\", \"" + seas_data + "\", \"" + media_list + "\")'>On Hold</a>" +
            "<a data-dismiss='modal' class='list-group-item text-light bg-dark modded' onclick='changeCategory(\"" + element_id + "\", \"" + random + "\", \"" + tr_id + "\", \"" + mod_id + "\", \"" + seas_drop_id + "\", \"" + ep_drop_id + "\", \"" + seas_data + "\", \"" + media_list + "\")'>Random</a>" +
            "<a data-dismiss='modal' class='list-group-item text-light bg-dark modded' onclick='changeCategory(\"" + element_id + "\", \"" + dropped + "\", \"" + tr_id + "\", \"" + mod_id + "\", \"" + seas_drop_id + "\", \"" + ep_drop_id + "\", \"" + seas_data + "\", \"" + media_list + "\")'>Dropped</a>" +
            "<a data-dismiss='modal' class='list-group-item text-light bg-dark modded' onclick='changeCategory(\"" + element_id + "\", \"" + plan_to_watch + "\", \"" + tr_id + "\", \"" + mod_id + "\", \"" + seas_drop_id + "\", \"" + ep_drop_id + "\", \"" + seas_data + "\", \"" + media_list + "\")'>Plan to Watch</a>"
        );
        $("#" + tr_id).prependTo("#tbody_WATCHING");
        $('.modal').modal("hide");
    }

    if (new_category === 'Completed') {
        var watching = 'Watching';
        var on_hold = 'On Hold';
        var random = 'Random';
        var dropped = 'Dropped';
        var plan_to_watch = 'Plan to Watch';

        $("#"+mod_id+ " a").filter(":contains('Watching')").remove()
        $("#"+mod_id+ " a").filter(":contains('Completed')").remove()
        $("#"+mod_id+ " a").filter(":contains('On Hold')").remove()
        $("#"+mod_id+ " a").filter(":contains('Random')").remove()
        $("#"+mod_id+ " a").filter(":contains('Dropped')").remove()
        $("#"+mod_id+ " a").filter(":contains('Plan to Watch')").remove()

        $("#"+mod_id).prepend(
            "<a data-dismiss='modal' class='list-group-item text-light bg-dark modded' onclick='changeCategory(\"" + element_id + "\", \"" + watching + "\", \"" + tr_id + "\", \"" + mod_id + "\", \"" + seas_drop_id + "\", \"" + ep_drop_id + "\", \"" + seas_data + "\", \"" + media_list + "\")'>Watching</a>" +
            "<a data-dismiss='modal' class='list-group-item text-light bg-dark modded' onclick='changeCategory(\"" + element_id + "\", \"" + on_hold + "\", \"" + tr_id + "\", \"" + mod_id + "\", \"" + seas_drop_id + "\", \"" + ep_drop_id + "\", \"" + seas_data + "\", \"" + media_list + "\")'>On Hold</a>" +
            "<a data-dismiss='modal' class='list-group-item text-light bg-dark modded' onclick='changeCategory(\"" + element_id + "\", \"" + random + "\", \"" + tr_id + "\", \"" + mod_id + "\", \"" + seas_drop_id + "\", \"" + ep_drop_id + "\", \"" + seas_data + "\", \"" + media_list + "\")'>Random</a>" +
            "<a data-dismiss='modal' class='list-group-item text-light bg-dark modded' onclick='changeCategory(\"" + element_id + "\", \"" + dropped + "\", \"" + tr_id + "\", \"" + mod_id + "\", \"" + seas_drop_id + "\", \"" + ep_drop_id + "\", \"" + seas_data + "\", \"" + media_list + "\")'>Dropped</a>" +
            "<a data-dismiss='modal' class='list-group-item text-light bg-dark modded' onclick='changeCategory(\"" + element_id + "\", \"" + plan_to_watch + "\", \"" + tr_id + "\", \"" + mod_id + "\", \"" + seas_drop_id + "\", \"" + ep_drop_id + "\", \"" + seas_data + "\", \"" + media_list + "\")'>Plan to Watch</a>"
        );
        $("#" + tr_id).prependTo("#tbody_COMPLETED");
        $('.modal').modal("hide");

        var season_data = JSON.parse("[" + seas_data + "]");
        var episode_drop = document.getElementById(ep_drop_id);

        var seasons_length = $('#'+seas_drop_id).children('option').length;
        console.log(seasons_length);
        var seasons_index = (seasons_length - 1);
        console.log(seasons_index);
        $('#'+seas_drop_id).prop('selectedIndex', seasons_index);

        episode_drop.length = 1;

        for (i = 2; i <= season_data[0][seasons_index]; i++) {
            let opt = document.createElement("option");
            opt.text = "Episode " + i;
            episode_drop.appendChild(opt);
        }
        $('#'+ep_drop_id).prop('selectedIndex', season_data[0][seasons_index]-1);
    }

    if (new_category === 'On Hold') {
        var completed = 'Completed';
        var watching = 'Watching';
        var random = 'Random';
        var dropped = 'Dropped';
        var plan_to_watch = 'Plan to Watch';

        $("#"+mod_id+ " a").filter(":contains('Watching')").remove()
        $("#"+mod_id+ " a").filter(":contains('Completed')").remove()
        $("#"+mod_id+ " a").filter(":contains('On Hold')").remove()
        $("#"+mod_id+ " a").filter(":contains('Random')").remove()
        $("#"+mod_id+ " a").filter(":contains('Dropped')").remove()
        $("#"+mod_id+ " a").filter(":contains('Plan to Watch')").remove()

        $("#"+mod_id).prepend(
            "<a data-dismiss='modal' class='list-group-item text-light bg-dark modded' onclick='changeCategory(\"" + element_id + "\", \"" + watching + "\", \"" + tr_id + "\", \"" + mod_id + "\", \"" + seas_drop_id + "\", \"" + ep_drop_id + "\", \"" + seas_data + "\", \"" + media_list + "\")'>Watching</a>" +
            "<a data-dismiss='modal' class='list-group-item text-light bg-dark modded' onclick='changeCategory(\"" + element_id + "\", \"" + completed + "\", \"" + tr_id + "\", \"" + mod_id + "\", \"" + seas_drop_id + "\", \"" + ep_drop_id + "\", \"" + seas_data + "\", \"" + media_list + "\")'>Completed</a>" +
            "<a data-dismiss='modal' class='list-group-item text-light bg-dark modded' onclick='changeCategory(\"" + element_id + "\", \"" + random + "\", \"" + tr_id + "\", \"" + mod_id + "\", \"" + seas_drop_id + "\", \"" + ep_drop_id + "\", \"" + seas_data + "\", \"" + media_list + "\")'>Random</a>" +
            "<a data-dismiss='modal' class='list-group-item text-light bg-dark modded' onclick='changeCategory(\"" + element_id + "\", \"" + dropped + "\", \"" + tr_id + "\", \"" + mod_id + "\", \"" + seas_drop_id + "\", \"" + ep_drop_id + "\", \"" + seas_data + "\", \"" + media_list + "\")'>Dropped</a>" +
            "<a data-dismiss='modal' class='list-group-item text-light bg-dark modded' onclick='changeCategory(\"" + element_id + "\", \"" + plan_to_watch + "\", \"" + tr_id + "\", \"" + mod_id + "\", \"" + seas_drop_id + "\", \"" + ep_drop_id + "\", \"" + seas_data + "\", \"" + media_list + "\")'>Plan to Watch</a>"
        );
        $("#" + tr_id).prependTo("#tbody_ON_HOLD");
        $('.modal').modal("hide");
    }

    if (new_category === 'Random') {
        var completed = 'Completed';
        var on_hold = 'On Hold';
        var watching = 'Watching';
        var dropped = 'Dropped';
        var plan_to_watch = 'Plan to Watch';

        $("#"+mod_id+ " a").filter(":contains('Watching')").remove()
        $("#"+mod_id+ " a").filter(":contains('Completed')").remove()
        $("#"+mod_id+ " a").filter(":contains('On Hold')").remove()
        $("#"+mod_id+ " a").filter(":contains('Random')").remove()
        $("#"+mod_id+ " a").filter(":contains('Dropped')").remove()
        $("#"+mod_id+ " a").filter(":contains('Plan to Watch')").remove()

        $("#"+mod_id).prepend(
            "<a data-dismiss='modal' class='list-group-item text-light bg-dark modded' onclick='changeCategory(\"" + element_id + "\", \"" + watching + "\", \"" + tr_id + "\", \"" + mod_id + "\", \"" + seas_drop_id + "\", \"" + ep_drop_id + "\", \"" + seas_data + "\", \"" + media_list + "\")'>Watching</a>" +
            "<a data-dismiss='modal' class='list-group-item text-light bg-dark modded' onclick='changeCategory(\"" + element_id + "\", \"" + completed + "\", \"" + tr_id + "\", \"" + mod_id + "\", \"" + seas_drop_id + "\", \"" + ep_drop_id + "\", \"" + seas_data + "\", \"" + media_list + "\")'>Completed</a>" +
            "<a data-dismiss='modal' class='list-group-item text-light bg-dark modded' onclick='changeCategory(\"" + element_id + "\", \"" + on_hold + "\", \"" + tr_id + "\", \"" + mod_id + "\", \"" + seas_drop_id + "\", \"" + ep_drop_id + "\", \"" + seas_data + "\", \"" + media_list + "\")'>On Hold</a>" +
            "<a data-dismiss='modal' class='list-group-item text-light bg-dark modded' onclick='changeCategory(\"" + element_id + "\", \"" + dropped + "\", \"" + tr_id + "\", \"" + mod_id + "\", \"" + seas_drop_id + "\", \"" + ep_drop_id + "\", \"" + seas_data + "\", \"" + media_list + "\")'>Dropped</a>" +
            "<a data-dismiss='modal' class='list-group-item text-light bg-dark modded' onclick='changeCategory(\"" + element_id + "\", \"" + plan_to_watch + "\", \"" + tr_id + "\", \"" + mod_id + "\", \"" + seas_drop_id + "\", \"" + ep_drop_id + "\", \"" + seas_data + "\", \"" + media_list + "\")'>Plan to Watch</a>"
        );
        $("#" + tr_id).prependTo("#tbody_RANDOM");
        $('.modal').modal("hide");
    }

    if (new_category === 'Dropped') {
        var completed = 'Completed';
        var on_hold = 'On Hold';
        var random = 'Random';
        var watching = 'Watching';
        var plan_to_watch = 'Plan to Watch';

        $("#"+mod_id+ " a").filter(":contains('Watching')").remove()
        $("#"+mod_id+ " a").filter(":contains('Completed')").remove()
        $("#"+mod_id+ " a").filter(":contains('On Hold')").remove()
        $("#"+mod_id+ " a").filter(":contains('Random')").remove()
        $("#"+mod_id+ " a").filter(":contains('Dropped')").remove()
        $("#"+mod_id+ " a").filter(":contains('Plan to Watch')").remove()

        $("#"+mod_id).prepend(
            "<a data-dismiss='modal' class='list-group-item text-light bg-dark modded' onclick='changeCategory(\"" + element_id + "\", \"" + watching + "\", \"" + tr_id + "\", \"" + mod_id + "\", \"" + seas_drop_id + "\", \"" + ep_drop_id + "\", \"" + seas_data + "\", \"" + media_list + "\")'>Watching</a>" +
            "<a data-dismiss='modal' class='list-group-item text-light bg-dark modded' onclick='changeCategory(\"" + element_id + "\", \"" + completed + "\", \"" + tr_id + "\", \"" + mod_id + "\", \"" + seas_drop_id + "\", \"" + ep_drop_id + "\", \"" + seas_data + "\", \"" + media_list + "\")'>Completed</a>" +
            "<a data-dismiss='modal' class='list-group-item text-light bg-dark modded' onclick='changeCategory(\"" + element_id + "\", \"" + on_hold + "\", \"" + tr_id + "\", \"" + mod_id + "\", \"" + seas_drop_id + "\", \"" + ep_drop_id + "\", \"" + seas_data + "\", \"" + media_list + "\")'>On Hold</a>" +
            "<a data-dismiss='modal' class='list-group-item text-light bg-dark modded' onclick='changeCategory(\"" + element_id + "\", \"" + random + "\", \"" + tr_id + "\", \"" + mod_id + "\", \"" + seas_drop_id + "\", \"" + ep_drop_id + "\", \"" + seas_data + "\", \"" + media_list + "\")'>Random</a>" +
            "<a data-dismiss='modal' class='list-group-item text-light bg-dark modded' onclick='changeCategory(\"" + element_id + "\", \"" + plan_to_watch + "\", \"" + tr_id + "\", \"" + mod_id + "\", \"" + seas_drop_id + "\", \"" + ep_drop_id + "\", \"" + seas_data + "\", \"" + media_list + "\")'>Plan to Watch</a>"
        );
        $("#" + tr_id).prependTo("#tbody_DROPPED");
        $('.modal').modal("hide");
    }

    if (new_category === 'Plan to Watch') {
        var completed = 'Completed';
        var on_hold = 'On Hold';
        var random = 'Random';
        var dropped = 'Dropped';
        var watching = 'Watching';

        $("#"+mod_id+ " a").filter(":contains('Watching')").remove()
        $("#"+mod_id+ " a").filter(":contains('Completed')").remove()
        $("#"+mod_id+ " a").filter(":contains('On Hold')").remove()
        $("#"+mod_id+ " a").filter(":contains('Random')").remove()
        $("#"+mod_id+ " a").filter(":contains('Dropped')").remove()
        $("#"+mod_id+ " a").filter(":contains('Plan to Watch')").remove()

        $("#"+mod_id).prepend(
            "<a data-dismiss='modal' class='list-group-item text-light bg-dark modded' onclick='changeCategory(\"" + element_id + "\", \"" + watching + "\", \"" + tr_id + "\", \"" + mod_id + "\", \"" + seas_drop_id + "\", \"" + ep_drop_id + "\", \"" + seas_data + "\", \"" + media_list + "\")'>Watching</a>" +
            "<a data-dismiss='modal' class='list-group-item text-light bg-dark modded' onclick='changeCategory(\"" + element_id + "\", \"" + completed + "\", \"" + tr_id + "\", \"" + mod_id + "\", \"" + seas_drop_id + "\", \"" + ep_drop_id + "\", \"" + seas_data + "\", \"" + media_list + "\")'>Completed</a>" +
            "<a data-dismiss='modal' class='list-group-item text-light bg-dark modded' onclick='changeCategory(\"" + element_id + "\", \"" + on_hold + "\", \"" + tr_id + "\", \"" + mod_id + "\", \"" + seas_drop_id + "\", \"" + ep_drop_id + "\", \"" + seas_data + "\", \"" + media_list + "\")'>On Hold</a>" +
            "<a data-dismiss='modal' class='list-group-item text-light bg-dark modded' onclick='changeCategory(\"" + element_id + "\", \"" + random + "\", \"" + tr_id + "\", \"" + mod_id + "\", \"" + seas_drop_id + "\", \"" + ep_drop_id + "\", \"" + seas_data + "\", \"" + media_list + "\")'>Random</a>" +
            "<a data-dismiss='modal' class='list-group-item text-light bg-dark modded' onclick='changeCategory(\"" + element_id + "\", \"" + dropped + "\", \"" + tr_id + "\", \"" + mod_id + "\", \"" + seas_drop_id + "\", \"" + ep_drop_id + "\", \"" + seas_data + "\", \"" + media_list + "\")'>Dropped</a>"
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