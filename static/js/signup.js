const signupForm = document.querySelector('#signup-form')
const errorDisplay = document.querySelector('.error')
const signupBtn = document.querySelector('#signup-btn')
const infoDisplay = document.querySelector('.info')


// form submission
signupForm.addEventListener('submit', async function(event) {
    event.preventDefault()
    // reset error display
    errorDisplay.textContent = ''

    // disable button
    signupBtn.disabled = true

    // read form 
    let data = {
        email: document.querySelector('#email').value.trim(),
        full_name: document.querySelector('#full-name').value.trim(),
        country: document.querySelector('#country').value.trim(),
        linkedin: document.querySelector('#linkedin').value.trim(),
        portfolio: document.querySelector('#portfolio').value.trim(),
        password: document.querySelector('#password').value.trim(),
        confirm_password: document.querySelector('#confirm-password').value.trim(),
        resume: document.querySelector('#resume').value.trim()
    }
    
    // validation
    if(data.country == '') {
        errorDisplay.textContent = 'Please select a country'
        signupBtn.disabled = false
        return
    }

    //// passwords must match
    if (data.password != data.confirm_password) {
        errorDisplay.textContent = 'Passwords do not match'
        signupBtn.disabled = false
        return
    }

    // signup
    // display feedback
    infoDisplay.textContent = 'Signing up...'
    let response = await fetch(
        '/auth/signup',
        {
            method: 'POST',
            body: JSON.stringify(data),
            headers: {
                'Content-type': 'Application/json'
            }
        }
    )
    infoDisplay.textContent = ''

    if(!response) {
        errorDisplay.textContent = 'Signup failed. Check your connection and try again'
        signupBtn.disabled = false
        return
    }

    if(!response.ok) {
        try{
            const data = await response.json()
            errorDisplay.textContent = data.detail
        }
        // incase response is not json
        catch(error) {
            console.log(error)
            errorDisplay.textContent = 'Failed to sign up. Try again'
        }
        signupBtn.disabled = false
        return 
    }

    infoDisplay.textContent = 'Signed up successfully'
    signupBtn.disabled = false

    setTimeout(() => {
        document.location.href = '/pages/dashboard'
    }, 1000)
})