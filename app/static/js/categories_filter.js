document.addEventListener("DOMContentLoaded", function () {
  document.getElementById("category-button").addEventListener("click", function () {
    filterByCategory();
  });
});

function filterByCategory(){
    // TODO(issue#67): Allow filter by category name
    const category = document.getElementById("category").value;

    const css = (!Number.isInteger(+category) || !category || 0 === category.length) ? `
    .event_line {
      display: grid;
      visibility: visible;
    }
    ` : `
    .event_line {
      display: none;
      visibility: hidden;
    }
    .event_line[data-name*="${category}" i] {
      display: grid;
      visibility: visible;
    }
    `;
    window.cssFilter.innerHTML = css;

    const allEvents = document.getElementsByClassName("event_line");
    for (event of allEvents) {
      event.parentNode.style.display = "none" ;
    }

    // Set wrapper div to display "block" if at least one child is visible
    for (event of allEvents) {
      if (window.getComputedStyle(event).display !== 'none') {
        event.parentNode.style.display = "block" ;
      }
    }
}