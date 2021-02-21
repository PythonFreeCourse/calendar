document.addEventListener("DOMContentLoaded", function () {
  document.getElementById("category-button").addEventListener("click", function () {
    filterByCategory();
  });
});

function filterByCategory(){
    // TODO(issue#67): Allow filter by category name
    const category = document.getElementById("category").value;

    const allEvents = document.getElementsByClassName("event_line");
    for (event of allEvents) {
      if (event.dataset.name == category)
      {
        event.style.display = "grid";
      }
      else {
        event.style.display = "none";
      }
      if (!Number.isInteger(+category) || !category || 0 === category.length) {
        event.style.display = "grid";
      }
      event.parentNode.style.display = "none" ;
    }

    // Set wrapper div to display "block" if at least one child is visible
    for (event of allEvents) {
      if (window.getComputedStyle(event).display !== 'none') {
        event.parentNode.style.display = "block" ;
      }
    }
}