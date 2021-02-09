function scrollTo(element) {
    window.scroll({
      behavior: 'smooth',
      left: 0,
      top: element.offsetTop
    });
}


var ev = document.getElementById("event.id");
if(ev) {
    ev.addEventListener("click", displayEvent);
}

function displayEvent(wantedevent) {
    fetch('/event/' + wantedevent)
    .then(function(response) {
        return response.text();
    })
    .then(function(body) {
        document.querySelector('#here').innerHTML = body;
        scrollTo(document.getElementById("here"));
    });
}