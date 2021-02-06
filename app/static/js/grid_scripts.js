function setToggle(elementClass, targetElement, classToAdd, lastIndex) {
    const allDays = document.getElementsByClassName(elementClass);
    const target = document.getElementById(targetElement);
    for (let i = lastIndex; i < allDays.length; ++i) {
        allDays[i].addEventListener("click", function () {
            target.classList.toggle(classToAdd);
        })
    }
}

function isMonthLoaded(monthId) {
    const allFirst = document.querySelectorAll('*[id^="01"]');
    for (let i = 0; i < allFirst.length; ++i) {
        if (allFirst[i].id === monthId) {
            return true;
        }
    }
    return false;
}

document.addEventListener(
    'DOMContentLoaded', function () {
        setToggle("day", "day-view", "day-view-visible", 0);
        setMonthNav();

        const dayAfter = document.getElementById("aft-month-title")
        dayAfter.addEventListener('click', function () {
            loadMonthBlockIfMissing(dayAfter);
        })
    }
)

function loadWeek(lastDay, index) {
    if (lastDay.dataset.last === "false") {
        return false;
    }
    lastDay.dataset.last = false;
    const path = '/calendar/month/add/' + lastDay.id;
    fetch(path).then(function (response) {
        return response.text();
    }).then(function (html) {
        document.getElementById("calender-grid").insertAdjacentHTML('beforeEnd', html);
        setToggle("day", "day-view", "day-view-visible", index);
    });
}

function getDaysBeforeN(date, n = 7) {
    const currentDate = new Date(date);
    currentDate.setDate(currentDate.getDate() - n);
    const day = currentDate.toLocaleString('en-US', { day: 'numeric' });
    const month = currentDate.toLocaleString('en-US', { month: 'long' });
    const year = currentDate.toLocaleString('en-US', { year: 'numeric' });
    return day + '-' + month + '-' + year;
}

function OnlyOnScreen(elements) {
    let first = null;
    for (let i = 0; i < elements.length; ++i) {
        elementRect = elements[i].getBoundingClientRect();
        if (elementRect.y > 0 && elementRect.y < 250) {
            if (i > 0) {
                first = elements[i - 1];
            } else {
                first = elements[i];
            }
            return [first, elements[i], elements[i + 1]];
        }
    }
}

function setAncore(link, elementToLink) {
    n = getDaysBeforeN(elementToLink.id);
    const targetLink = document.getElementById(link);
    const elementId = elementToLink.id.split("-");
    targetLink.innerHTML = elementId[1].slice(0, 3) + " " + elementId[2].slice(2, 4);
    targetLink.href = '#' + n;
}

function setMonthNav() {
    const allFirst = document.querySelectorAll('*[id^="01"]');
    currentMonthsId = OnlyOnScreen(allFirst);
    if (currentMonthsId) {
        setAncore("pre-month-title", currentMonthsId[0]);
        setAncore("current-month-title", currentMonthsId[1]);
        setAncore("aft-month-title", currentMonthsId[2]);
    }
}

window.addEventListener(
    'scroll', function () {
        const tolerance = 10;
        if (window.scrollY + window.innerHeight + tolerance < document.documentElement.scrollHeight) {
            return false;
        }
        const allDays = document.getElementsByClassName('day');
        const lastDay = allDays[allDays.length - 1];
        loadWeek(lastDay, allDays.length);
    }
)

window.addEventListener('wheel', function () {
    setMonthNav();
})

