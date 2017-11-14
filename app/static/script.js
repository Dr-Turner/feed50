$(function() {

    // removing "new" status off new items in the feed once the user clicks on them
    $(".panel-success").click(function() {
        $(this).addClass("panel-default").removeClass("panel-success");
        // removing " (new)" off of the title
        var title = $(this).find('a')[0].text;
    	if (title.endsWith(" (new)")) {
            $(this).find('a')[0].text = title.slice(0, -6);
        }
    });
});