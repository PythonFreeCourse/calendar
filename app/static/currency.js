function getCurrency(baseCurrency, dateToday) {
    const showCurrencyElement = document.getElementById("showCurrency")
    const currencyViewElement = document.getElementById("currencyView");
    const currencyButtonElement = document.getElementById("currencyButton");
    currencyViewElement.innerHTML = "";

    function getResponse(yourUrl) {
        var httpRequest = new XMLHttpRequest();
        httpRequest.open("GET", yourUrl, false);
        httpRequest.send(null);
        return httpRequest.responseText;
    }

    const data = JSON.parse(getResponse('https://api.exchangeratesapi.io/' + dateToday + '?base=' + baseCurrency));
    if (!('rates' in data)) {
        return false;
    }

    if (showCurrencyElement.style.display == 'none') {
        showCurrencyElement.style.display = 'block';
    }

    var listItem = document.createElement("li");
    listItem.className = "list-group-item title_size_small";
    const baseItem = document.createElement("strong");
    baseItem.innerHTML = "BASE: " + baseCurrency;
    listItem.appendChild(baseItem);
    currencyViewElement.appendChild(listItem);

    for (key in data.rates) {
        if (key !== baseCurrency) {
            listItem = document.createElement("li");
            listItem.className = "list-group-item title_size_small";
            var linkItem = document.createElement("a");
            linkItem.setAttribute("id", key);
            linkItem.setAttribute("href", "javascript:void(0)");
            linkItem.innerText = key;
            listItem.appendChild(linkItem);
            var ratesItem = document.createElement("div");
            ratesItem.setAttribute("style", "display: inline;")
            ratesItem.innerHTML = ": " + data.rates[key];
            listItem.appendChild(ratesItem);
            currencyViewElement.appendChild(listItem);
        }
    }

    listItem = document.createElement("li");
    listItem.className = "list-group-item title_size_small";
    const dateItem = document.createElement("strong");
    dateItem.innerHTML = dateToday;
    listItem.appendChild(dateItem);
    currencyViewElement.appendChild(listItem);
    return true;
}