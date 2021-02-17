CURSORS_PATH = "/media/cursors/";
window.addEventListener("load", get_cursor_choices);

/**
 * @summary This function gets cursor choices from the db.
 */
function get_cursor_choices() {
  let request = new XMLHttpRequest();
  request.open("GET", "/cursor/load_cursor", true);
  request.onload = change_cursor;
  request.send();
}

/**
 * @summary This function changes the primary cursor and the secondary
 * cursor according to users' choices.
 */
function change_cursor() {
  let cursor_settings = JSON.parse(JSON.parse(this.response));
  let primary_cursor = cursor_settings["primary_cursor"];
  let primary_cursor_val =
    "url(" + CURSORS_PATH + primary_cursor + ")" + ", auto";
  let secondary_cursor = cursor_settings["secondary_cursor"];
  let secondary_cursor_val =
    "url(" + CURSORS_PATH + secondary_cursor + ")" + ", auto";
  if (primary_cursor != "default.cur") {
    primary_val = primary_cursor_val;
  } else {
    primary_val = "";
  }
  document.body.style.cursor = primary_val;
  let links = document.querySelectorAll("a, button, input, select, label");
  if (secondary_cursor != "default.cur") {
    secondary_val = secondary_cursor_val;
  } else {
    secondary_val = "";
  }
  links.forEach((element) => {
    element.style.cursor = secondary_val;
  });
}
