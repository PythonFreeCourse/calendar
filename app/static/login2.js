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
    await postLogin(user)
}

// loginForm.addEventListener("submit", submitLogin)
await postLogin()
async function postLogin() {
    try {
        // Create request to api service
        const req = await fetch('http://127.0.0.1:8000/auth/jwt/login', {
            method: 'POST',
            headers: { "Content-Type": "application/x-www-form-urlencoded" },
            body: `username=${form.username.data}&password=${form.password.data}`
        });
        const res = await req.json();
        if (req.status === 400){
            console.log("Bad credentials");
        }
        if (req.status === 422){
            console.log("Missing details");
        }
        if (req.status === 200){
            localStorage.setItem('okLoginMessage', "hi, you successfully sign in")
            function user() {
                var x = "/login?response=" + res
                const xhr = new XMLHttpRequest();
                xhr.open("GET", x, true);
            xhr.send();
            }
            console.log(res)
            setCookie("fastapiusersauth4", res["access_token"])
            window.location.href = "http://127.0.0.1:8000/protected";
        }
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