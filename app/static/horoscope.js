function sendSignDescription(singName) {
  const sign = singName.toLowerCase();
  const signData = "https://aztro.sameerkumar.website/?sign=" + sign +
    "&day=today";
  const xhr = new XMLHttpRequest();
  xhr.open("POST", signData, true);
  xhr.onload = function () {
    let jsonObject = JSON.parse(this.responseText);
    let element = document.getElementById("daily_horoscope");
    let str = jsonObject.description;
    element.innerHTML = str;
  };
  xhr.send();
}


function addEventsAfterPageLoaded() {
  const elements = document.getElementsByClassName("sign");
  Array.from(elements).forEach((element) => {
    let singName = element.name;
    element.addEventListener("click", function () {
      sendSignDescription(singName);
    }, false);
  });
}

document.addEventListener("DOMContentLoaded", addEventsAfterPageLoaded);