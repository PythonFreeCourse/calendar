const registerMessageBox = document.querySelector("#registerSuccessful")

if (localStorage.getItem("okRegisterMessage") !== null){
    // localStorage.getItem('okRegisterMessage')) {
    registerMessageFunc(localStorage.getItem('okRegisterMessage'))
    localStorage.removeItem('okRegisterMessage')
}

function registerMessageFunc(text){
    registerMessageBox.textContent = text
    registerMessageBox.style.display="block";
}