async function daily_horoscope(singName) {
    sign = singName.toLowerCase();
    var x = 'https://aztro.sameerkumar.website/?sign=' + sign + '&day=today'
    const xhr = new XMLHttpRequest();
    xhr.open("POST", x, true);
    xhr.onload = function() {
        let obj = JSON.parse(this.responseText);
        let daily = document.getElementById('daily_horoscope');
        let str = obj.description;
        daily.innerHTML = str;
    }
    xhr.send();
}

var elements = document.getElementsByClassName('sign');

function addEventsLoop() {
    Array.from(elements).forEach((element) => {
        let singName = element.name;
        element.addEventListener('click', function() {
            daily_horoscope(singName);
        }, false);
    });
}

document.addEventListener('DOMContentLoaded', addEventsLoop);