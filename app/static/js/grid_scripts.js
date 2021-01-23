document.addEventListener(
    'DOMContentLoaded',
    function () {
        var all_days = document.querySelectorAll('.day'), i;
        for (i = 0; i < all_days.length; ++i) {
            all_days[i].onclick = function () {
                var daily_event = document.querySelector("#day-display");
                if (daily_event.style.flex === '0 1 30%') {
                    daily_event.style.opacity = '0';
                    daily_event.style.flex = '0 0 0';
                }
                else {
                    daily_event.style.opacity = '1';
                    daily_event.style.flex = '0 1 30%';
                }
            };

        }
    });


