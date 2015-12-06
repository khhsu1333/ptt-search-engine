
$(function() {
    $('.card').click(function() {
        url = $(this).attr('data-url');
        open(url)
    });

    $('.cache').click(function(event) {
        event.stopPropagation();

        url = $(this).attr('data-url');
        open(url)
    });
});
