function getDailyJoke() {
  fetch('/getjoke')
    .then(response => response.json())
    .then(data => alert(data.value.joke));
}
