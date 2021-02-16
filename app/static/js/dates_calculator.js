window.onload = function () {
  document.getElementById("CalcBtn").addEventListener("click", hiddenDifference);
}

function hiddenDifference() {
    if (document.getElementById("endDate").value == '') {
        swal("Expected end date");
        return;
    }
    let date1 = document.getElementById("startDate").value;
    const date2 = new Date(document.getElementById("endDate").value);
    if (date1 != '') {
        date1 = new Date(date1);
    }
    else {
        date1 = Date.now();
    }
    const diffDates = Math.abs(date2 - date1);
    const diffInDays = Math.ceil(diffDates / (1000 * 60 * 60 * 24));
    document.getElementById("demo").innerText = "The difference: " + (diffInDays) + " days";
}
