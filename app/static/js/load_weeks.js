const container = document.querySelector('.calender-grid')
let template = null

function load_week() {
    var all_days = document.querySelectorAll('.day')
    var last_day = all_days[all_days.length - 1].id
    url = '/calendar/' + last_day

    fetch(url, { method: 'POST' })
        .then((response) => {
            template = response.data
        });
    console.log(template)
}

window.addEventListener(
    'scroll', function () {
        if (window.scrollY + window.innerHeight + 1 >= document.documentElement.scrollHeight) {
            load_week()
        }
    }
)

