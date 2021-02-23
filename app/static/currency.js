function getCurrency(baseCurrency, dateToday) {
  const showCurrencyElement = document.getElementById("showCurrency")
  const currencyViewElement = document.getElementById("currencyView");
  const myUrl = 'https://api.exchangeratesapi.io/' + dateToday + '?base=' + baseCurrency

  async function getResponse(myUrl) {
    let response = await fetch(myUrl);
    if (response.ok) {
      let result = await response.json();
      currencyViewElement.innerHTML = "";
      showCurrencyElement.dataset.visible = "1";
      return result;
    }
  }

  getResponse(myUrl)
    .then(result => buildCurrencyList(result));

  function buildCurrencyList(data) {
    function getListItem() {
      const listItem = document.createElement("li");
      listItem.className = "list-group-item title-size-small";
      return listItem;
    }

    function createBoldListItem(fieldString, currViewElem) {
      const listItem = getListItem();
      const boldItem = document.createElement("strong");
      boldItem.innerHTML = fieldString;
      listItem.appendChild(boldItem);
      currViewElem.appendChild(listItem);
    }

    function getAnchorItem() {
      const linkItem = document.createElement("a");
      linkItem.setAttribute("href", "javascript:void(0)");
      linkItem.setAttribute("id", key);
      linkItem.innerText = key;
      return linkItem;
    }

    function getRatesItem(fieldString) {
      let ratesItem = document.createElement("div");
      ratesItem.setAttribute("style", "display: inline;")
      ratesItem.innerHTML = fieldString;
      return ratesItem;
    }

    function createAllElements(dataRates, baseCurr, currViewElem) {
      for (key in dataRates) {
        if (key !== baseCurr) {
          let listItem = getListItem();
          let linkItem = getAnchorItem();
          let ratesItem = getRatesItem(": " + dataRates[key]);
          listItem.appendChild(linkItem);
          listItem.appendChild(ratesItem);
          currViewElem.appendChild(listItem);
        }
      }
    }

    // Create Base currency list item
    createBoldListItem("BASE: " + baseCurrency, currencyViewElement);
    // Create all rates list items
    createAllElements(data.rates, baseCurrency, currencyViewElement);
    // Create date list item
    createBoldListItem(dateToday, currencyViewElement);

    return true;
  }
}