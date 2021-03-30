document.addEventListener("DOMContentLoaded", () => {
  get_games_btn = document.getElementById("get-games");
  get_games_btn.addEventListener("click", function (e) {
    const formData = new FormData();
    formData.append("from-date", document.getElementById("from-date").value);
    formData.append("to-date", document.getElementById("to-date").value);

    fetch("/game-releases/get_releases_by_dates", {
      method: "post",
      body: formData,
    })
      .then(function (response) {
        return response.text();
      })
      .then(function (body) {
        document.querySelector("#content-div").innerHTML = body;
      });
  });
});
