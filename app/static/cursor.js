const CURSORS_PATH = "/media/cursors/";
window.addEventListener("load", get_cursor_choices);

/**
 * @summary This function gets cursor choices from the db.
 */
function get_cursor_choices() {
  const request = new XMLHttpRequest();
  request.open("GET", "/cursor/load_cursor", true);
  request.onload = change_cursor;
  request.send();
}

/**
 * @summary This function changes the primary cursor and the secondary
 * cursor according to users' choices.
 */
function change_cursor() {
  const cursor_settings = JSON.parse(JSON.parse(this.response));
  const primary_cursor_choice = cursor_settings["primary_cursor"];
  const primary_cursor_path = `url(${CURSORS_PATH}${primary_cursor_choice}), auto`;
  const secondary_cursor_choice = cursor_settings["secondary_cursor"];
  const secondary_cursor_path = `url(${CURSORS_PATH}${secondary_cursor_choice}), auto`;
  const primary_cursor = primary_cursor_choice !== "default.cur" ? primary_cursor_path : "";
  const secondary_cursor = secondary_cursor_choice !== "default.cur" ? secondary_cursor_path : "";
  document.body.style.cursor = primary_cursor;
  const links = document.querySelectorAll("a, button, input, select, label");
  links.forEach((element) => {
    element.style.cursor = secondary_cursor;
  });
}
