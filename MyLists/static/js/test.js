
function test(element_id, media_type, add_cat, media_name) {
    $body = $("body");
    $.ajax ({
        type: "POST",
        url: "/add_to_medialist",
        contentType: "application/json",
        data: JSON.stringify({ add_cat: add_cat, element_id: element_id, media_type: media_type, media_name: media_name }),
        dataType: "json",
        success: function(response) {
            console.log("ok");
        }
    });
}