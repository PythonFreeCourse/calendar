/*

function getView(view: string) {
    const path = '/' + view + '/2021-1-3';
    fetch(path)
        .then((response => response.text())
        .then(function (html) {
            view = document.getElementById("calendarview");
            view.replaceWith(html);
        });
}
/*
var monthview = document.getElementById("month-view-button");
var weekview = document.getElementById("week-view-button");
var dayview = document.getElementById("day-view-button");
*/

function changeview(view) {
    alert(view);
  }
