// ----------- Responsive icon --------------
function hamburger() {
    var icon = document.getElementById("achievements_topnav");
    if (icon.className === "topnav") {
        icon.className += " responsive";
    } else {
        icon.className = "topnav";
    }
}

// ------------- Achievements ---------------
function openAchievement(evt, type) {
    var i, tabcontent, tablinks;

    tabcontent = document.getElementsByClassName("tabcontent");
    for (i = 0; i < tabcontent.length; i++) {
        tabcontent[i].style.display = "none";
    }

    tablinks = document.getElementsByClassName("tablinks");
    for (i = 0; i < tablinks.length; i++) {
        tablinks[i].className = tablinks[i].className.replace(" active", "");
    }

    document.getElementById(type).style.display = "block";
    evt.currentTarget.className += " active";

    var hide = evt.currentTarget.parentElement;
    if ($(hide).hasClass('topnav responsive')) {
        $(hide).attr('class', 'topnav');
    }
}

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