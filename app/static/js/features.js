function display(rows, target) {
    return true;
}

function searchFeature(event, rows) {
    const searchValue = event.target.value;
    if (!searchValue) {
        return false;
    } else {
        const result = rows.filter(
            row => { return row.getElementsByClassName("row-feature-name")[0].innerHTML.includes(searchValue) }
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

function setSearchBox() {
    searchBox = document.getElementsByClassName("search-input");
    if (!searchBox) {
        return false;
    }
    searchBox[0].addEventListener('input', function (evt) {
        const rows = getAvailable();
        const result = searchFeature(evt, rows);
        display(result);
    });
}

document.addEventListener(
    'DOMContentLoaded', function () {
        setSearchBox();
    }
)

