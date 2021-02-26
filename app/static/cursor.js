const CURSORS_PATH = "/media/cursors/";

// These must be global so the mutationObserver could access them.
let primary_cursor;
let secondary_cursor;

window.addEventListener("load", init);

/**
 * @summary In charge of initialising the customization of the cursor.
 */
function init() {
  get_cursor_choices();
  initMutationObserver();
}

/**
 * @summary This function gets cursor choices from the db.
 */
function get_cursor_choices() {
  const request = new XMLHttpRequest();
  request.open("GET", "/cursor/load", true);
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
  primary_cursor =
    primary_cursor_choice !== "default.cur" ? primary_cursor_path : "";
  secondary_cursor =
    secondary_cursor_choice !== "default.cur" ? secondary_cursor_path : "";
  document.body.style.cursor = primary_cursor;
  const links = document.querySelectorAll("a, button, input, select, label");
  links.forEach((element) => {
    element.style.cursor = secondary_cursor;
  });
}

/**
 * @summary Sets up mutation observer to follow dynamically added links
 */
function initMutationObserver() {
  const config = {
    childList: true,
    subtree: true,
  };
  const observer = new MutationObserver(mutate);
  observer.observe(document, config);
}

/**
 * @summary This function identifies a new element for the secondary cursor,
 * and sets it according to the users' choices.
 */
function mutate(mutationList) {
  const links = ["a", "button", "input", "select", "label"];
  for (let mutation of mutationList) {
    if (mutation.type == "childList") {
      handle_potential_links(mutation.addedNodes, links);
    }
  }
}

/**
 * @summary Helper function to the mutate function which
 * on creation of new nodes in the DOM, if it is a link - changes its'
 * style.
 */
function handle_potential_links(nodes, links) {
  nodes.forEach((element) => {
    if (
      typeof(element.tagName) !== "undefined" &&
      links.includes(element.tagName.toLowerCase())
    ) {
      element.setAttribute("style", secondary_cursor);
    }
  });
}
