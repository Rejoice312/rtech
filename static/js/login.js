const loginForm = document.querySelector('#login-form')
const errorDisplay = document.querySelector('.error')
const infoDisplay = document.querySelector('.info')
const loginBtn = document.querySelector('#login-btn')

loginForm.addEventListener('submit', async (event) =>{
    event.preventDefault()
    loginBtn.disabled = true
    let data
    let response

    errorDisplay.textContent = ''
    // read data
    data = {
        email: document.querySelector('#email').value,
        password: document.querySelector('#password').value
    }

    // login
    infoDisplay.textContent = 'Logging in...'
    response = await fetch(
        '/auth/login',
        {
            method: 'POST',
            body: JSON.stringify(data),
            headers: {
                'Content-Type': 'application/json'
            }
        }
    )
    
    // try displaying response. or default error if response is not json
    if(!response.ok) {
        infoDisplay.textContent = ''
        try{
            data = await response.json()
            errorDisplay.textContent = data.detail
            console.log(JSON.stringify(data))
        }
        catch(error) {
            console.log(error)
            errorDisplay.textContent = 'Failed to login. Check you internet connection and try again later'
        }
        loginBtn.disabled = false
        return
    }

    infoDisplay.textContent = 'Logged in successfully'
    loginBtn.disabled = false

    
    setTimeout(() => {
        document.location.href = '/pages/dashboard'
    }, 500)
    
})