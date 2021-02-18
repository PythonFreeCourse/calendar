function OnlyOnScreen(elements) {
    for (let i = 0; i < elements.length; ++i) {
        elementRect = elements[i].getBoundingClientRect();
        if (elementRect.y > 0) {
            return elements[i];
        }
    }
}

function dateToId(date, format = 'en-US') {
    let day = date.toLocaleString(format, { day: 'numeric' });
    day = "0" + day;
    const month = date.toLocaleString(format, { month: 'long' });
    const year = date.toLocaleString(format, { year: 'numeric' });
    return day.slice(-2) + '-' + month + '-' + year;
}

function stringToDate(string) {
    stringSplit = string.split("-");
    return new Date(stringSplit[1] + ' ' + stringSplit[0] + ', ' + stringSplit[2])
}

function getDateInNMonths(date, n) {
    let currentDate = stringToDate(date);
    return new Date(currentDate.setMonth(currentDate.getMonth() + n));
}

function getDateInNDays(date, n) {
    let currentDate = stringToDate(date);
    return new Date(currentDate.setDate((currentDate.getDate() + n) - 1));
}

function displayMonthYear(id) {
    const idParts = id.split("-");
    return idParts[1].slice(0, 3) + " " + idParts[2].slice(2, 4);
}

function setMonthNav() {
    const allFirst = document.querySelectorAll('[id^="01"]');
    const currentMonth = OnlyOnScreen(allFirst);
    for (let i = -2; i < 3; ++i) {
        const date = getDateInNMonths(currentMonth.id, i);
        const dateId = dateToId(date);
        const link = document.getElementById("month" + i);
        link.href = '#' + dateId;
        link.innerHTML = displayMonthYear(dateId);
    }
}

function jump(link) {
    setTimeout(function () {
        document.getElementById(link).click();
    }, 100);
}

function calcDaysToLoad(number, weekDays = 7, monthBlock = 6) {
    if (number % weekDays === 0) {
        return number * weekDays;
    }
    const division = Math.ceil(number / weekDays);
    if (division < monthBlock) {
        return (monthBlock + 1) * weekDays;
    }
    return division * weekDays;
}

function loadDaysIfNeeded(dateId, link) {
    const allFirst = Array.from(document.querySelectorAll('[id^="01"]'));
    const allId = allFirst.map(x => x.id);
    if (allId.includes(dateId)) {
        return false;
    }
    let deltaDays = 0;
    const targetDay = stringToDate(dateId);
    const firstDay = stringToDate(allId[0]);
    if (firstDay > targetDay) {
        deltaDays = parseInt((firstDay - targetDay) / (1000 * 60 * 60 * 24), 10);
        callLoadWeek(calcDaysToLoad(deltaDays), false);
    } else {
        const lastDay = stringToDate(allId[allId.length - 1]);
        deltaDays = parseInt((targetDay - lastDay) / (1000 * 60 * 60 * 24), 10);
        callLoadWeek(calcDaysToLoad(deltaDays));
    }
    jump(link);
}

function setMonthNavClick() {
    const MonthNavNodes = document.getElementById('months-navigation').children;
    for (let i = 0; i < MonthNavNodes.length; ++i) {
        node = MonthNavNodes[i];
        if (node.tagName === 'A') {
            node.addEventListener('click', function () {
                const id = this.getAttribute("href").slice(1);
                loadDaysIfNeeded(id, this.id);
                setTimeout(setMonthNav, 100);
            });
        }
    }
}

document.addEventListener(
    'DOMContentLoaded', function () {
        setMonthNav();
        setMonthNavClick();
    }
)