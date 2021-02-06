function getCelebs(dateToday) {
    const celebCards = document.getElementById("celebCards");

    fetch('https://www.imdb.com/search/name/?birth_monthday=' + dateToday)
        .then(function (response) {
            return response.text();
        }).then(function (html) {
            celebCards.innerHTML = "";
            const parser = new DOMParser();
            const doc = parser.parseFromString(html, 'text/html');

            function getNames() {
                let namesArray = new Array();
                const names = doc.querySelectorAll('h3.lister-item-header');
                for (let i = 0; i < 12; i++) {
                    namesArray.push(names[i].innerText.trim().substr(5).trim());
                }
                return namesArray;
            }

            function getImages() {
                let imagesArray = new Array();
                const images = doc.querySelectorAll('div.lister-item-image a img');
                for (let i = 0; i < 12; i++) {
                    imagesArray.push(images[i].getAttribute("src"));
                }
                return imagesArray;
            }

            function getLinks() {
                let linksArray = new Array();
                const links = doc.querySelectorAll('div.lister-item-image a');
                for (let i = 0; i < 12; i++) {
                    linksArray.push(links[i].getAttribute("href"));
                }
                return linksArray;
            }

            function getJobs() {
                let jobsArray = new Array();
                const jobs = doc.querySelectorAll("p.text-muted");
                for (let i = 0; i < 12; i++) {
                    jobsArray.push(jobs[i].innerText.trim().split("|")[0].trim());
                }
                return jobsArray;
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
                for (let i = 0; i < 12; i++) {
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

            const namesArray = getNames();
            const imagesArray = getImages();
            const linksArray = getLinks();
            const jobsArray = getJobs();

            buildCards(celebCards);
        }).catch(() => {
            celebCards.innerHTML = "Failed to load Celebrity birthdays."
        });
}