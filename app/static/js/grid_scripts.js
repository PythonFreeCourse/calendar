function setToggle(elementClass, targetElement, classToAdd) {
    const allDays = document.getElementsByClassName(elementClass);
    for (let i = window['lastIndex']; i < allDays.length; ++i) {
        allDays[i].addEventListener("click", function () {
            const target = document.getElementById(targetElement);
            target.classList.toggle(classToAdd);
        })
    }
    window['lastIndex'] += allDays.length - window['lastIndex'];
}


document.addEventListener(
    'DOMContentLoaded', function () {
        window['lastIndex'] = 0;
        window['last'] = 0;
        setToggle("day", "day-view", "day-view-visible");
    }
)

function loadWeek(lastDay) {
    if (lastDay === window['last']) {
        return false;
    }
    const path = '/calendar/month/' + lastDay;
    const newDays = document.createElement('html');
    window['last'] = lastDay;
    fetch(path).then(function (response) {
        return response.text();
    }).then(function (html) {
        const newDiv = document.createElement("div");
        newDays.innerHTML = html
        newDiv.appendChild(newDays);
        document.getElementById("calender-grid").append(newDays);
        setToggle("day", "day-view", "day-view-visible");
    });
}

window.addEventListener(
    'scroll', function () {
        const tolerance = 1;
        if (window.scrollY + window.innerHeight + tolerance < document.documentElement.scrollHeight) {
            return false;
        }
        const allDays = document.querySelectorAll('.day');
        const lastDay = allDays[allDays.length - 1].id;
        loadWeek(lastDay);
    }
)