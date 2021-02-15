/*function getPath(view) {
    if view == "week"
    '/' + view + '/2021-1-3'
    return path;
}*/

function changeview(view) {
    const path = '/' + view + '/2021-1-3';
    fetch(path).then(function (response) {
        return response.text();
      }).then(function (html) {
        view = document.getElementById("calendarview");
        view.innerHTML = html
      });
}
