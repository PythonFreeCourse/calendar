const celebCards = document.getElementById("celebCards");

function getCelebs(dateToday) {
  const numberOfCelebs = 12;
  const celebsUrl = 'https://www.imdb.com/search/name/?birth_monthday=' + dateToday;

  fetch(celebsUrl)
    .then(function (response) {
      return response.text();
    }).then(function (html) {
    celebCards.innerText = "";
    const parser = new DOMParser();
    const doc = parser.parseFromString(html, 'text/html');
    getCelebsData(doc);
  }).catch(() => {
    celebCards.innerText = "Failed to load Celebrity birthdays.";
  });

  function getCelebsData(doc) {
    function getDataByType(myArray, dataType, selectorData) {
      if (dataType === "names") {
        myArray.push(selectorData.innerText.trim().substr(5).trim());
      } else if (dataType === "images") {
        myArray.push(selectorData.getAttribute("src"));
      } else if (dataType === "links") {
        myArray.push(selectorData.getAttribute("href"));
      } else if (dataType === "jobs") {
        myArray.push(selectorData.innerText.trim().split("|")[0].trim());
      }
    }

    function getArray(selector, dataType) {
      let myArray = [];
      const selectorData = doc.querySelectorAll(selector);
      for (let i = 0; i < numberOfCelebs; i++) {
        getDataByType(myArray, dataType, selectorData[i]);
      }
      return myArray;
    }

    function getTopDiv() {
      let card = document.createElement("div");
      card.className = "card top-div";
      return card;
    }

    function getImgElement(img) {
      let imgElement = document.createElement("img");
      imgElement.className = "card-img-top";
      imgElement.setAttribute("src", img);
      return imgElement
    }

    function getDivFooter() {
      let divFooter = document.createElement("div");
      divFooter.className = "card-footer div-footer";
      return divFooter
    }

    function getSmallElement(anchorElement, jobElement) {
      let smallElement = document.createElement("small");
      smallElement.className = "text-muted";
      smallElement.appendChild(anchorElement);
      smallElement.appendChild(jobElement);
      return smallElement;
    }

    function getAnchorElement(link, name) {
      let anchorElement = document.createElement("a");
      anchorElement.setAttribute("href", "https://www.imdb.com" + link);
      anchorElement.setAttribute("title", name);
      anchorElement.setAttribute("target", "_blank");
      anchorElement.innerText = name;
      return anchorElement;
    }

    function getJobElement(job) {
      let jobElement = document.createElement("div");
      jobElement.className = "div-job";
      jobElement.innerText = " | " + job;
      return jobElement;
    }

    function buildCards(celebCards) {
      for (let i = 0; i < numberOfCelebs; i++) {
        const card = getTopDiv();
        const imgElement = getImgElement(imagesArray[i]);
        card.appendChild(imgElement);

        const divFooter = getDivFooter();
        const anchorElement = getAnchorElement(linksArray[i], namesArray[i]);
        const jobElement = getJobElement(jobsArray[i]);
        const smallElement = getSmallElement(anchorElement, jobElement);
        divFooter.appendChild(smallElement);

        card.appendChild(divFooter);
        celebCards.appendChild(card);
      }
    }

    const namesArray = getArray("h3.lister-item-header", "names");
    const imagesArray = getArray("div.lister-item-image a img", "images");
    const linksArray = getArray("div.lister-item-image a", "links");
    const jobsArray = getArray("p.text-muted", "jobs");
    buildCards(celebCards);
  }
}

window.addEventListener('load', function () {
  getCelebs(celebCards.dataset.today);
});