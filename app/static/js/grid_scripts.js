function set_toggle(cl1, target, insert) {
    let all_days = document.getElementsByClassName(cl1);
    for (let i = 0; i < all_days.length; ++i) {
        all_days[i].onclick = function () {
            let daily_event = document.getElementById(target);
            daily_event.classList.toggle(insert);
        }
    }
}

document.addEventListener('DOMContentLoaded', function () {
    set_toggle("day", "day-view", "day-view-visible");
    const container = document.querySelector('.calender-grid');
})

const anticipating = 1;
const last = null;

function load_week(last_day) {
    if (last_day != last) {
        const url = '/calendar/month/' + last_day;
        const last = last_day;

        fetch(url).then(function (response) {
            return response.text();
        }).then(function (html) {
            const new_days = document.createElement('html');
            new_days.innerHTML = html;
            document.getElementById("calender-grid").append(new_days);
            set_toggle("day", "day-view", "day-view-visible");
        });
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