document.onload = function () {
    const container = document.querySelector('.calender-grid');
}

const anticipating = 1;
const last = null;

function open_daily(new_days) {
    let all_days = new_days.getElementsByClassName('day'), i;
    for (i = 0; i < all_days.length; ++i) {
        all_days[i].onclick = function () {
            let daily_event = document.getElementById("day-view");
            daily_event.classList.toggle("day-view-visible");
        };
    }
    return new_days;
}

function load_week(last_day) {
    if (last_day != last) {
        const url = '/calendar/' + last_day;
        const last = last_day;

        fetch(url).then(function (response) {
            return response.text();
        }).then(function (html) {
            const new_days = document.createElement('html');
            new_days.innerHTML = html;
            open_daily(new_days);
            document.getElementById("calender-grid").append(new_days);
        })
    }
}

window.addEventListener(
    'scroll', function () {
        if (window.scrollY + window.innerHeight + anticipating >= document.documentElement.scrollHeight) {
            const all_days = document.querySelectorAll('.day');
            const last_day = all_days[all_days.length - 1].id;
            load_week(last_day);
        }
    }
)