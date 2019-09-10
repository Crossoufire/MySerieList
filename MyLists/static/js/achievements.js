
// ------------- Show details ---------------
$(".projects > li > a").on("click", function(e) {
    e.preventDefault();
    var li = $(this).parent(),
    li_height = li.height(),
    details = li.find(".details"),
    details_height = details.height(),
    new_height = details_height + 40;
    li.toggleClass("current").animate({paddingBottom: new_height}, {duration: 200, queue: false}).siblings().removeClass("current");
    $(".projects li:not(.current)").animate({paddingBottom: '0'}, {duration: 200, queue: false }).find(".details").slideUp(200);
    $(".current").find(".details").slideDown(200);
});