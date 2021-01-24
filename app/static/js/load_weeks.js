const container = document.querySelector('.calender-grid')
const anticipating = 1
const last = null

function load_week(last_day) {
    if (last_day != last) {
        req = $.ajax({
            url: '/calendar/' + last_day,
            type: 'GET'
        })
        const last = last_day
        req.done(function (data) {
            $(".calender-grid").append(data);
        });
    }
}


window.addEventListener(
    'scroll', function () {
        if (window.scrollY + window.innerHeight + anticipating >= document.documentElement.scrollHeight) {
            var all_days = document.querySelectorAll('.day')
            var last_day = all_days[all_days.length - 1].id
            load_week(last_day)
        }
    }
)

