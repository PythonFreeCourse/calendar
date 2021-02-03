function findselected() {
    let deactivate = 0;
    let result = document.querySelector('input[name="outOfOffice"]:checked').value;
    if (result == deactivate) {
        document.getElementById("start_date").setAttribute('disabled', true);
        document.getElementById("end_date").setAttribute('disabled', true);
    }
    else {
        document.getElementById("start_date").removeAttribute('disabled');
        document.getElementById("end_date").removeAttribute('disabled');
    }
}