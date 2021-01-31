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
        // .then((response) => console.log(response))
        // .catch((error) => console.log(error));
        console.log(req)
        // 
        // Create request to api service
        // const req = await fetch('http://localhost:8000/auth/cookie/login', {
        //     method: 'POST',
        //     // headers: { "Content-Type": "application/x-www-form-urlencoded" },
        //     headers: { "Content-Type": "multipart/form-data" },
        //     body: `username=${user.username}&password=${user.password}`
        // });
        // const res = await req.json();
        // if (req.status === 400){
        //     console.log("Bad credentials");
        // }
        // if (req.status === 422){
        //     console.log("Missing details");
        // }
        // if (req.status === 200){
        //     localStorage.setItem('okLoginMessage', `${user.username}, you successfully sign in`)
            
        //     console.log('success')
        //     // setCookie("fastapiusersauth", res["access_token"])
        //     // window.location.href = "http://127.0.0.1:8000/protected";
        // }
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