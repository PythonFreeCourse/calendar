function daily_horoscope(sign) {
    var x = 'https://aztro.sameerkumar.website/?sign=' + sign + '&day=today'
    const xhr = new XMLHttpRequest();
    xhr.open("POST", x, true);
    xhr.onload = function() {
        obj = JSON.parse(this.responseText);
        let daily = document.getElementById("daily_horoscope");
        str = `${obj.description}`;
        daily.innerHTML = str;
    }
    xhr.send();
}