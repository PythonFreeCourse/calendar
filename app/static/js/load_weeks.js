const container = document.querySelector('.calender-grid')
const anticipating = 1
const last = null

function load_week(last_day) {
    if (last_day != last) {
        var url = '/calendar/' + last_day
        const last = last_day

        fetch(url).then(function (response) {
            return response.text();
        }).then(function (html) {
            var div = document.createElement('html');
            div.innerHTML = html
            document.getElementById("calender-grid").append(div);
        })
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