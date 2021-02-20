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

function display(elements, targetID, empty) {
    if (!empty) {
        deleteElements(targetID);
    }
    appendElement(elements, targetID);
}

function searchFeature(searchValue, elements) {
    const result = elements.filter(
        element => {
            return element.getElementsByClassName("row-feature-name")[0].innerHTML.toLowerCase().includes(searchValue)
        }
    );
    return result;
}

function getAvailable(elements) {
    let availables = [];
    for (let i = 0; i < elements.length; ++i) {
        const element = elements[i];
        if (element.dataset.state === "available") {
            availables.push(element);
        }
    }
    return availables;
}

function setSearchBox(targetID) {
    const rows = document.getElementsByClassName("feature-row");
    const searchBox = document.getElementsByClassName("search-input");
    searchBox[0].addEventListener(
        'input', function (evt) {
            console.log(rows);
            const value = evt.target.value.trim().toLowerCase();
            if (!value) {
                display(rows, targetID, true);
            } else {
                const result = searchFeature(value, rows);
                display(result, targetID, false);
            }
        });
}

function moveColumn(rows) {
    const row = this.parentElement;
    const category = row.parentElement;
    if (category.id === "available-features") {
        this.innerHTML = "REMOVE";
        this.classList.remove("background-green");
        this.classList.add("background-red");
        row.dataset.state = "installed";
        document.getElementById("installed-features").appendChild(row);
    } else {
        this.innerHTML = "ADD";
        this.classList.remove("background-red");
        this.classList.add("background-green");
        row.dataset.state = "available";
        document.getElementById("available-features").appendChild(row);
    }
}

function setRemoveAdd(className) {
    const rows = document.getElementsByClassName(className);
    for (let i = 0; i < rows.length; ++i) {
        const row = rows[i];
        const button = row.getElementsByClassName("feature-button")[0];
        button.addEventListener('click', moveColumn);
    }
}

document.addEventListener(
    'DOMContentLoaded', function () {
        setSearchBox("available-features");
        setRemoveAdd("feature-row");
    }
)

