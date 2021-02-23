const FULL_HEART = "../media/full_heart.png";
const EMPTY_HEART = "../media/empty_heart.png";

// Adding event listener
window.addEventListener("load", function () {
  let hearts = Array.from(document.getElementsByClassName("heart"));
  hearts.forEach((heart_element) => {
    if (heart_element) {
      heart_element.addEventListener("click", function () {
        onHeartClick(heart_element);
      });
    }
  });
});

/**
 * @summary This function is a handler for the event of heart-click.
 * Whenever a user clicks on a heart icon, in case of empty heart:
 * saves quote in favorites, as well as changing
 * the heart icon from empty to full.
 * In case of full heart:
 * Removes it and switch back to empty heart icon.
 * Uses the save_or_remove_quote function to handle db operations.
 */
function onHeartClick(heart_element) {
  const quote_id = heart_element.dataset.qid;
  if (heart_element.dataset.heart == "off") {
    heart_element.src = FULL_HEART;
    heart_element.dataset.heart = "on";
    save_or_remove_quote(quote_id, true);
  } else {
    heart_element.src = EMPTY_HEART;
    heart_element.dataset.heart = "off";
    save_or_remove_quote(quote_id, false);
    if (heart_element.classList.contains("favorites")) {
      heart_element.parentNode.parentNode.remove();
    }
  }
}

/**
 * @summary Saves or removes a quote from favorites.
 */
function save_or_remove_quote(quote_id, to_save) {
  const method = to_save ? "post" : "delete";
  let xhr = new XMLHttpRequest();
  quote_id = parseInt(quote_id);
  xhr.open(method, "/");
  xhr.setRequestHeader("Content-Type", "application/x-www-form-urlencoded");
  xhr.send(`quote_id=${quote_id}`);
}
