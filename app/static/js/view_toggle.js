function refreshview() {
  location.reload();
}

function set_views_styles(view, element_id) {
  if (element_id == "calender-view") {
    dayviewdiv = document.getElementById("day-view");
    dayviewdiv.style.display = 'none';
  }
  if (element_id == "day-view"){
    view.classList.add("day-view-class");
    view.style.overflow = "scroll";
  }
}


function change_view(view, day, element_id) {
  const path = '/' + view + '/' + day;
  fetch(path).then(function (response) {
      return response.text();
    }).then(function (html) {
      view = document.getElementById(element_id);
      view.innerHTML = html;
      set_views_styles(view, element_id);
    }
  );
}
