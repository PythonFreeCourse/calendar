const FULL_HEART = "../../media/full_heart.png";
const EMPTY_HEART = "../../media/empty_heart.png";

// Adding event listener
window.addEventListener("load", function () {
  const quoteContainer = document.getElementById("quote-container");
  if (!quoteContainer) {
    return;
  }
  const isConnected = quoteContainer.dataset.connected;
  if (isConnected !== "True") {
    return;
  }
  const fullHeart = document.getElementsByClassName("full-heart")[0];
  const emptyHeart = document.getElementsByClassName("empty-heart")[0];
  if (fullHeart) {
    fullHeart.classList.toggle("full-heart");
  } else if (emptyHeart) {
    emptyHeart.classList.toggle("empty-heart");
  }

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
  const url = method == "post" ? "/quotes/save" : "/quotes/delete";
  const xhr = new XMLHttpRequest();
  quote_id = parseInt(quote_id);
  xhr.open(method, url);
  xhr.setRequestHeader("Content-Type", "application/x-www-form-urlencoded");
  xhr.send(`quote_id=${quote_id}`);
}
