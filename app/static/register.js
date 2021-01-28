const registerForm = document.querySelector("#registerForm")
const errorBox = document.querySelector("#errorBox")

// const userExistError = document.querySelector("#user_exist")
const passwordLengthError = document.querySelector("#password_length")
// const confirmPasswordError = document.querySelector("#confirmPasswordError")

function validateFields(user){
    if (user.password !== user.confirm_password){
        showError("passwords don't match")
        return false
    }
    if (user.username.length < 3 || user.username.length > 20){
        showError("Username must contain between 3 to 20 characters")
        return false
    }
    if (user.password.length < 3 || user.password.length > 20){
        showError("Username must contain between 3 to 20 characters")
        return false
    }
    if (user.full_name.length < 3 || user.full_name.length > 20){
        showError("Full name must contain between 3 to 20 characters")
        return false
    }
    if (!validateEmail(user.email)){
        showError("Email address must be valid")
        return false
    }
return true
}

function validateEmail(email) {
    const re = /^(([^<>()[\]\\.,;:\s@"]+(\.[^<>()[\]\\.,;:\s@"]+)*)|(".+"))@((\[[0-9]{1,3}\.[0-9]{1,3}\.[0-9]{1,3}\.[0-9]{1,3}\])|(([a-zA-Z\-0-9]+\.)+[a-zA-Z]{2,}))$/;
    return re.test(String(email).toLowerCase());
}

function showError(text){
    errorBox.textContent = text
    errorBox.style.display="block";
}

async function submitSignUp(e){
    e.preventDefault();
    const { username, full_name, password, confirm_password, email, description } = e.target.elements;
    let user = {
        username: username.value,
        full_name: full_name.value,
        email: email.value,
        password: password.value,
        confirm_password: confirm_password.value,
        description: description.value,
        is_active: true,
        is_superuser: false,
        is_verified: false
    };
    if (validateFields(user)){
        delete user["confirm_password"];
        await post(user)
    }
}
registerForm.addEventListener("submit", submitSignUp)



async function post(user) {
    try {
        // Create request to api service
        const req = await fetch('http://127.0.0.1:8000/auth/register', {
            method: 'POST',
            headers: { 'Content-Type':'application/json' },
            
            // format the data
            body: JSON.stringify( user ),
        });
        
        const res = await req.json();
        // console.log(res)
        if (req.status === 400){
            showError("User already registered");
        }
        if (req.status === 201){
            localStorage.setItem('okRegisterMessage', `${user.username}, you successfully registered!`)
            window.location.href = "http://127.0.0.1:8000/login";
        }
        // Log success message
        // console.log(res);                
    } catch(err) {
        
        console.error(`ERROR: ${err}`);
    }
}

// Call your function
// post() // with your parameter of Course




// console.log(registerForm)