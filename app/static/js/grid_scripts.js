function setToggle(elementClass, targetElement, classToAdd, lastIndex) {
    const allDays = document.getElementsByClassName(elementClass);
    const target = document.getElementById(targetElement);
    for (let i = lastIndex; i < allDays.length; ++i) {
        allDays[i].addEventListener("click", function () {
            target.classList.toggle(classToAdd);
        })
    }
}

document.addEventListener(
    'DOMContentLoaded', function () {
        setToggle("day", "day-view", "day-view-visible", 0);
        weekScroll();
    }
)

function loadWeek(lastDay, index) {
    if (lastDay.dataset.last === "false") {
        return false;
    }
    lastDay.dataset.last = false;
    const path = '/calendar/month/' + lastDay.id;
    fetch(path).then(function (response) {
        return response.text();
    }).then(function (html) {
        document.getElementById("calender-grid").insertAdjacentHTML('beforeEnd', html);
        setToggle("day", "day-view", "day-view-visible", index);
    });
}

function weekScroll() {
    grid = document.getElementById("calender-grid");
    grid.addEventListener(
        'scroll', function () {
            const tolerance = 1;
            if (grid.scrollY + grid.innerHeight + tolerance < grid.scrollHeight) {
                return false;
            }
            const allDays = document.getElementsByClassName('day');
            const lastDay = allDays[allDays.length - 1];
            loadWeek(lastDay, allDays.length);
        }
    )
}