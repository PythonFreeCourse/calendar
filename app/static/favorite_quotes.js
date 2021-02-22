// Adding event listeners
let hearts = Array.from(document.getElementsByClassName("heart"));
window.addEventListener("load", function () {
  hearts.forEach((heart) => {
    if (heart) {
      heart.addEventListener("click", onHeartClick);
    }
  });
});

const FULL_HEART = "../media/full_heart.png";
const EMPTY_HEART = "../media/empty_heart.png";

/**
 * @summary This function is a handler for the event of heart-click.
 * Whenever a user clicks on a heart icon, in case of empty heart:
 * saves quote in favorites, as well as changing
 * the heart icon from empty to full.
 * In case of full heart:
 * Removes it and switch back to empty heart icon.
 * Uses the save_or_remove_quote function to handle db operations.
 */
function onHeartClick() {
  const quote = this.parentNode.previousElementSibling.innerText;
  if (this.dataset.heart == "off") {
    this.src = FULL_HEART;
    this.dataset.heart = "on";
    save_or_remove_quote(quote, true);
  } else {
    this.src = EMPTY_HEART;
    this.dataset.heart = "off";
    save_or_remove_quote(quote, false);
    if (this.classList.contains("favorites")) {
      this.parentNode.parentNode.remove();
    }
  }
}

/**
 * @summary Saves or removes a quote from favorites.
 */
function save_or_remove_quote(quote, to_save) {
  const method = to_save ? "post" : "delete";
  quote = encodeURIComponent(quote);
  let xhr = new XMLHttpRequest();
  xhr.open(method, "/");
  xhr.setRequestHeader("Content-Type", "application/x-www-form-urlencoded");
  xhr.send(`quote=${quote}`);
}
