function setToggle(elementClass, targetElement, classToAdd, lastIndex) {
    const allDays = document.getElementsByClassName(elementClass);
    for (let i = lastIndex; i < allDays.length; ++i) {
        allDays[i].addEventListener("click", function () {
            const target = document.getElementById(targetElement);
            target.classList.toggle(classToAdd);
        })
    }
}

document.addEventListener(
    'DOMContentLoaded', function () {
        setToggle("day", "day-view", "day-view-visible", 0);
    }
)

function loadWeek(lastDay, index) {
    if (lastDay.dataset.last === "false") {
        return false;
    }
    lastDay.dataset.last = false;
    const path = '/calendar/month/' + lastDay.id;
    alert(path);
    const newDays = document.createElement('html');
    fetch(path).then(function (response) {
        return response.text();
    }).then(function (html) {
        const newDiv = document.createElement("div");
        newDays.innerHTML = html
        newDiv.appendChild(newDays);
        document.getElementById("calender-grid").append(newDays);
        setToggle("day", "day-view", "day-view-visible", index);
    });
}

window.addEventListener(
    'scroll', function () {
        const tolerance = 100;
        if (window.scrollY + window.innerHeight + tolerance < document.documentElement.scrollHeight) {
            return false;
        }
        const allDays = document.querySelectorAll('.day');
        const lastDay = allDays[allDays.length - 1];
        loadWeek(lastDay, allDays.length);
    }
)