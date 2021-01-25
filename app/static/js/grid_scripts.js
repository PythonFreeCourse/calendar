document.addEventListener(
    'DOMContentLoaded',
    function () {
        let all_days = document.getElementsByClassName('day'), i;
        for (i = 0; i < all_days.length; ++i) {
            all_days[i].onclick = function () {
                let daily_event = document.getElementById("day-view");
                daily_event.classList.toggle("day-view-visible");
            };
        }
    });




