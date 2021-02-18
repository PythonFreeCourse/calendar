function appendElement(elements, targetID) {
    const target = document.getElementById(targetID);
    for (let i = 0; i < elements.length; ++i) {
        target.append(elements[i]);
    }
}

function deleteElements(targetID) {
    const target = document.getElementById(targetID).children;
    const length = target.length;
    for (let i = 0; i < length; ++i) {
        target[0].remove();
    }
}

function display(elements, targetID) {
    deleteElements(targetID);
    appendElement(elements, targetID);
}

function searchFeature(event, rows, targetID) {
    const searchValue = event.target.value.trim().toLowerCase();
    if (!searchValue) {
        appendElement(rows, targetID);
    } else {
        const result = rows.filter(
            row => {
                return row.getElementsByClassName("row-feature-name")[0].innerHTML.toLowerCase().includes(searchValue)
            }
        );
        return result;
    }
}

function getAvailable() {
    let allAva = []
    const allAvailable = document.getElementsByClassName("feature-row");
    for (let i = 0; i < allAvailable.length; ++i) {
        if (allAvailable[i].dataset.state === "available") {
            allAva.push(allAvailable[i]);
        }
    }
    return allAva;
}

function setSearchBox(targetID) {
    searchBox = document.getElementsByClassName("search-input");
    if (!searchBox) {
        return false;
    }
    const rows = getAvailable();
    searchBox[0].addEventListener('input', function (evt) {
        if (evt.which === null) {
            appendElement(rows, targetID)
        }
        deleteElements(targetID);
        const result = searchFeature(evt, rows, targetID);
        display(result, targetID);

    });
}


function setAdd(className) {
    const allRows = document.getElementsByClassName(className);
    for (let i = 0; i < allRows.length; ++i) {
        if (allRows[i].dataset.state === "available") {
            setAdd(allRows[i]);
        } else {
            setRemove(allRows[i]);
        }
    }
}

document.addEventListener(
    'DOMContentLoaded', function () {
        setSearchBox("available-features");
        setAdd(className);
    }
)

