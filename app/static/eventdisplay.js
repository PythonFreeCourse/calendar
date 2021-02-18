function scrollTo(element) {
    window.scroll({
      behavior: 'smooth',
      left: 0,
      top: element.offsetTop
    });
}

document.addEventListener('DOMContentLoaded', () => {
    const chosen_button = document.getElementsByClassName('event-btn');
    for (let i = 0; i < chosen_button.length; i++) {
        chosen_button[i].addEventListener("click", function(e) {
        let clickedElem = e.target.id
            fetch('/event/edit')
            .then(function(response) {
                return response.text();
            })
            .then(function(body) {
                document.querySelector('#event_block').innerHTML = body;
                scrollTo(document.getElementById("event_block"));
            });
        });
    }
});