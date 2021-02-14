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
        date1 = Date.now()
    }
    const diffTime = Math.abs(date2 - date1);
    const diffDays = Math.ceil(diffTime / (1000 * 60 * 60 * 24));
    document.getElementById("demo").innerHTML = "The difference: " + (diffDays) + " days";
}
