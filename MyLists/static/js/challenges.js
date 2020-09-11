

function challenge(challenge_id) {
    $('.loading-chal').show();

    $.ajax ({
        type: "POST",
        url: "/add_challenges",
        contentType: "application/json",
        data: JSON.stringify({challenge_id: challenge_id}),
        dataType: "json",
        success: function() {
            $('.add-chal').show('slow').delay(2000).fadeOut();
        },
        error: function() {
            error_ajax_message('Error trying to add the challenge. Please try again later.');
        },
        complete: function() {
            $('.loading-chal').hide();
        }
    });
}