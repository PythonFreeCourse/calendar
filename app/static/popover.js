// Enable bootstrap popovers

var popoverList = popoverTriggerList.map(function (popoverTriggerEl) {
    return new bootstrap.Popover(popoverTriggerEl, {
        container: 'body',
        html: true,
        sanitize: false
    })
});
