// Adding event listeners
let hearts = Array.from(document.getElementsByClassName("heart"));
window.addEventListener("load", function () {
  hearts.forEach((heart) => {
    if (heart) {
      heart.addEventListener("click", on_heart_click);
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
function on_heart_click() {
  const quote = this.parentNode.previousElementSibling.innerText;
  const author_element = this.parentNode;

  if (author_element.innerHTML.includes("\\")) {
    const author = author_element.innerHTML.split("\\ ")[1].split("\n")[0];
  }
  if (this.src.split("/").pop() == "empty_heart.png") {
    this.src = "../media/full_heart.png";
    save_or_remove_quote(1, quote, true);
  } else {
    this.src = "../media/empty_heart.png";
    save_or_remove_quote(1, quote, false);
    if (this.classList.contains("favorites")) {
      this.parentNode.parentNode.remove();
      this.parentNode.remove();
      this.remove();
    }
  }
}

/**
 * @summary Saves or removes a quote from favorites.
 */
function save_or_remove_quote(user_id, quote, to_save) {
  method = to_save ? "post" : "delete";
  quote = encodeURIComponent(quote);
  let xhr = new XMLHttpRequest();
  xhr.open(method, "/");
  xhr.setRequestHeader("Content-Type", "application/x-www-form-urlencoded");
  xhr.send(`user_id=${user_id}&quote=${quote}`);
}
