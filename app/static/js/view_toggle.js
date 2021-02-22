function refreshview() {
  location.reload();
}

function close_the_view() {
  dayviewdiv = document.getElementById("day-view");
  dayviewdiv.classList.remove("day-view-class", "day-view-limitions", "day-view-visible");
  dayviewdiv.innerHTML = '';
}

function set_views_styles(view_element, element_id) {
  if (element_id == "day-view"){
    view_element.classList.add("day-view-class", "day-view-limitions");
  }
}


function change_view(view, day, element_id) {
  if (element_id == "calendarview") {
    close_the_view();
  }
  const path = '/' + view + '/' + day;
  fetch(path).then(function (response) {
      return response.text();
    }).then(function (html) {
      view_element = document.getElementById(element_id);
      view_element.innerHTML = html;
      set_views_styles(view_element, element_id);
    }
  );
}
