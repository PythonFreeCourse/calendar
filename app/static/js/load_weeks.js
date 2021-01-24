const container = document.querySelector('.calender-grid')
const anticipating = 1

function load_week() {
    var all_days = document.querySelectorAll('.day')
    var last_day = all_days[all_days.length - 1].id
    console.log(last_day)
    req = $.ajax({
        url: '/calendar/' + last_day,
        type: 'GET'
    })

    req.done(function (data) {
        $(".calender-grid").append(data);
    });
}

window.addEventListener(
    'scroll', function () {
        if (window.scrollY + window.innerHeight + anticipating >= document.documentElement.scrollHeight) {
            load_week()
        }
    }
)

