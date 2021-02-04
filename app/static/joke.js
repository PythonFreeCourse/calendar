function makejoke() {
  fetch('/joke')
    .then(response => response.json())
    .then(data => alert(data.text));
}
