function refreshview() {
  location.reload();
}

function close_the_view() {
  dayviewdiv = document.getElementById("day-view");
  dayviewdiv.classList.remove("day-view-class", "day-view-limitions", "day-view-visible");
  dayviewdiv.innerText = '';
}

function set_views_styles(view_element, element_id) {
  if (element_id == "day-view") {
      view_element.classList.add("day-view-class", "day-view-limitions");
      btn = document.getElementById('close-day-view');
      btn.addEventListener("click", function() {
          close_the_view();
      });
  }
}

function change_view(view, day, element_id) {
  if (element_id == "calendarview") {
      close_the_view();
  }
  const path = `/${view}/${day}`;
  fetch(path).then(function(response) {
      return response.text();
  }).then(function(html) {
      view_element = document.getElementById(element_id);
      view_element.innerHTML = html;
      set_views_styles(view_element, element_id);
  });
}

function set_toggle_view_btns(btn, view) {
  dayview_btn = document.getElementById(btn);
  day = dayview_btn.name;
  dayview_btn.addEventListener('click', function() {
      change_view(view, day, "calendarview");
  });
}

function set_days_view_open() {
  const Days = document.getElementsByClassName('day');
  for (let i = 0; i < Days.length; i++) {
      let day = Days[i].title;
      Days[i].addEventListener('click', function() {
          change_view('day', day, 'day-view');
      });
  }
}


document.addEventListener(
  'DOMContentLoaded',
  function() {
      set_toggle_view_btns('week-view-button', 'week');
      set_toggle_view_btns('day-view-button', 'day');
      month = document.getElementById('month-view-button');
      month.addEventListener('click', function() {
          refreshview();
      });
      set_days_view_open();
  }
)
