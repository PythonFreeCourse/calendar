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
        event.dataset.value = "visible";
      }
      else {
        event.dataset.value = "hidden";
      }
      if (!Number.isInteger(+category) || !category || 0 === category.length) {
        event.dataset.value = "visible";
      }
      event.parentNode.dataset.value = "hidden";
    }

    // Set wrapper div to display "visible" if at least one child is visible.
    for (event of allEvents) {
      if (event.dataset.value === "visible") {
        event.parentNode.dataset.value = "visible";
      }
    }
}