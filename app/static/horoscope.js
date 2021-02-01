async function daily_horoscope(singName) {
    sign = singName.toLowerCase();
    console.log(singName)

    var x = 'https://aztro.sameerkumar.website/?sign=' + sign + '&day=today'
    const xhr = new XMLHttpRequest();
    xhr.open("POST", x, true);
    xhr.onload = function() {

        obj = JSON.parse(this.responseText);
        let daily = document.getElementById('daily_horoscope');
        str = `${obj.description}`;
        console.log(str);
        daily.innerHTML = str;
    }
    xhr.send();
}

var elements = document.getElementsByClassName('sign');

function myScript() {
    Array.from(elements).forEach((element) => {
        let singName = element.name;
        element.addEventListener('click', function() {
            daily_horoscope(singName);
        }, false);
    });
}

document.addEventListener('DOMContentLoaded', myScript);