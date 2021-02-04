const registerMessageBox = document.querySelector("#registerSuccessful")
const loginForm = document.querySelector("#loginForm")

if (localStorage.getItem("okRegisterMessage") !== null){
    // localStorage.getItem('okRegisterMessage')) {
    registerMessageFunc(localStorage.getItem('okRegisterMessage'))
    localStorage.removeItem('okRegisterMessage')
}

function registerMessageFunc(text){
    registerMessageBox.textContent = text
    registerMessageBox.style.display="block";
}

async function submitLogin(e){
    e.preventDefault();
    const { username, password } = e.target.elements;
    let user = {
        username: username.value,
        password: password.value,
    };
    const formData = new FormData();
    formData.set('username', user.username);
    formData.set('password', user.password);
    await postLogin(formData)
}

loginForm.addEventListener("submit", submitLogin)

async function postLogin(formData) {
    console.log(formData)
    try {
        const req = await axios.post(
            'http://localhost:8000/auth/cookie/login',
            formData,
            {
                headers: {
                    'Content-Type': 'multipart/form-data',
                },
            },
        )
        console.log(req)
    } catch(err) {
        
        console.error(`ERROR: ${err}`);
    }
}

function setCookie(cname, cvalue) {
    var d = new Date();
    d.setTime(d.getTime() + (3600*100));
    var expires = "expires="+ d.toUTCString();
    document.cookie = cname + "=" + cvalue + ";" + expires + ";path=/";
  }