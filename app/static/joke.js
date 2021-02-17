function makejoke() {
  fetch('/joke')
    .then(response => response.json())
    .then(data => alert(data.text));
}


function addEventsAfterPageLoaded() {
  const element = document.getElementById("a-joke");
  element.addEventListener("click", makejoke, false);
}


document.addEventListener("DOMContentLoaded", addEventsAfterPageLoaded);