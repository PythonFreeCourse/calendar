document.addEventListener(
    'DOMContentLoaded',
    function () {
        var all_days = document.querySelectorAll('.day'), i;
        for (i = 0; i < all_days.length; ++i) {
            all_days[i].onclick = function () {
                var daily_event = document.getElementById("day-view");
                daily_event.classList.toggle("day-view-visible");
            };
        }
    });




