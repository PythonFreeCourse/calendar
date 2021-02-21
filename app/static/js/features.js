function displayResult(rows, elements) {
    const rowsArray = Array.from(rows);
    const elementsArray = Array.from(elements);
    rowsArray.map(row => {
        if (elementsArray.includes(row)) {
            return row.classList.remove("invisible");
        } else {
            return row.classList.add("invisible");
        }
    });
}

function searchFeature(searchValue, elements) {
    const elementsArray = Array.from(elements);
    const result = elementsArray.filter(element => {
        return element.getElementsByClassName("row-feature-name")[0].innerHTML.toLowerCase().includes(searchValue);
    });
    return result;
}

function setSearchBox() {
    const searchBox = document.getElementsByClassName("search-input");
    searchBox[0].addEventListener(
        'input', function (evt) {
            const rows = document.getElementsByClassName("feature-row");
            const value = evt.target.value.trim().toLowerCase();
            if (!value) {
                Array.from(rows).map(element => element.classList.remove("invisible"));
            } else {
                const result = searchFeature(value, rows);
                displayResult(rows, result);
            }
        });
}

function updateFollowers(element, add = true) {
    const followers = element.getElementsByClassName("followers")[0];
    const followersNum = parseInt(followers.innerText);
    if (add) {
        followers.innerText = followersNum + 1;
    } else if (followersNum > 0) {
        followers.innerText = followersNum - 1;
    }
}

function move(button, element) {
    const category = element.parentElement;
    if (category.id === "available-features") {
        button.innerHTML = "REMOVE";
        button.classList = "button remove-button";
        element.dataset.state = "installed";
        document.getElementById("installed-features").appendChild(element);
        updateFollowers(element);
    } else {
        button.innerHTML = "ADD";
        button.classList = "button add-button";
        element.dataset.state = "available";
        document.getElementById("available-features").appendChild(element);
        updateFollowers(element, false);
    }
}

function setPath(action, url) {
    if (action === "ADD") {
        return new URL('/features/add', url);
    }
    return new URL('/features/delete', url);
}

function update() {
    const action = this.innerText;
    const parent = this.parentElement;
    const featureId = this.parentElement.id;
    const url = window.location.origin;
    let path = setPath(action, url);
    const formData = new FormData();
    formData.append('feature_id', featureId);
    fetch(path,
        {
            body: formData,
            method: "post"
        }
    ).then(response => {
        response.json();
        move(this, parent);
    });
}

function setFeatures() {
    const rows = document.getElementsByClassName("feature-row");
    for (let i = 0; i < rows.length; ++i) {
        const row = rows[i];
        const button = row.getElementsByClassName("button")[0];
        button.addEventListener('click', update);
    }
}

function setInformation() {
    let allInfo = document.getElementsByClassName("info-icon");
    Array.from(allInfo).map(element => {
        const parent = element.parentElement;
        const infoBox = parent.getElementsByClassName("information")[0];
        element.addEventListener("click", function () {
            if (infoBox.style.display === "block") {
                infoBox.style.display = "none";
            } else {
                infoBox.style.display = "block";
            }
        })
    });
}

document.addEventListener(
    'DOMContentLoaded', function () {
        setSearchBox();
        setFeatures();
        setInformation();
    }
)

