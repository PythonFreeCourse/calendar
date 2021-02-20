function setToggle(
    elementClass, targetElement, classToAdd,
    index, elementsToLoad
) {
    const allElements = document.getElementsByClassName(elementClass);
    const target = document.getElementById(targetElement);
    for (let i = 0; i < elementsToLoad; ++i) {
        allElements[index + i].addEventListener("click", function () {
            target.classList.toggle(classToAdd);
        })
    }
}

function isMonthLoaded(monthId) {
    const allFirst = document.querySelectorAll('[id^="01"]');
    for (let i = 0; i < allFirst.length; ++i) {
        if (allFirst[i].id === monthId) {
            return true;
        }
    }
    return false;
}

document.addEventListener(
    'DOMContentLoaded', function () {
        const allDays = document.getElementsByClassName('day');
        setToggle("day", "day-view", "day-view-visible", 0, allDays.length);
        weekScroll();
    }
)

function loadWeekAfter(baseUrl, day, index, daysToLoad) {
    if (day.dataset.last === "false") {
        return false;
    }
    day.dataset.last = false;

    let path = new URL('/calendar/month/add/' + day.id, baseUrl);
    params = { days: daysToLoad };
    Object.keys(params).forEach(key => path.searchParams.append(key, params[key]))

    fetch(path).then(function (response) {
        return response.text();
    }).then(function (html) {
        document.getElementById("calender-grid").insertAdjacentHTML('beforeEnd', html);
        setToggle("day", "day-view", "day-view-visible", index, daysToLoad);
    });
}

function loadWeekBefore(baseUrl, day, daysToLoad) {
    let path = new URL('/calendar/month/add/' + day, baseUrl);
    params = { days: daysToLoad };
    Object.keys(params).forEach(key => path.searchParams.append(key, params[key]))

    fetch(path).then(function (response) {
        return response.text();
    }).then(function (html) {
        document.getElementById("calender-grid").insertAdjacentHTML('afterbegin', html);
        setToggle("day", "day-view", "day-view-visible", 0, daysToLoad);
    });
}

function callLoadWeek(daysToLoad = 42, end = true) {
    let day = null;
    const url = window.location.origin;
    const allDays = document.getElementsByClassName('day');
    if (end) {
        day = allDays[allDays.length - 1];
        loadWeekAfter(url, day, allDays.length, daysToLoad);
    } else {
        day = dateToId(getDateInNDays(allDays[0].id, daysToLoad * -1))
        loadWeekBefore(url, day, daysToLoad);
    }
    setTimeout(setMonthNav, 200);
}

function weekScroll() {
    grid = document.getElementById("calender-grid");
    grid.addEventListener(
        'scroll', function () {
            const tolerance = 1;
            if (grid.scrollY + grid.innerHeight + tolerance < grid.scrollHeight) {
                return false;
            }
            callLoadWeek();
        }
    )
    grid.addEventListener('wheel', function () {
        if (this.scrollTop === 0) {
            callLoadWeek(42, end = false);
        }
    })
}