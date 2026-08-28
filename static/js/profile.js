const error_display = document.querySelector('.error')
const info_display = document.querySelector('.info')
const edit_btn = document.querySelector('#edit-details-btn')
const edit_details_form = document.querySelector('#edit-details-form')
const edit_form_submit_btn = document.querySelector('#edit-details-form > button')


edit_btn.addEventListener('click', () => {
    edit_details_form.classList.toggle('hidden')
})


edit_details_form.addEventListener('submit', async (event) => {
    event.preventDefault()
    error_display.textContent = ''
    info_display.textContent = 'Editing details...'
    edit_form_submit_btn.disabled = true

    // read form
    const data = {
        full_name: document.querySelector('#full-name').value.trim(),
        country: document.querySelector('#country').value.trim(),
        linkedin: document.querySelector('#linkedin').value.trim(),
        portfolio: document.querySelector('#portfolio').value.trim(),
        application_email: document.querySelector('#application-email').value.trim(),
        resume: document.querySelector('#resume')
    }

    const response = await fetch(
        '/users/me/edit',
        {
            method: 'PATCH',
            body: JSON.stringify(data),
            headers: {
                'Content-Type': 'application/json'
            }
        }
    )
    info_display.textContent = ''

    if(!response.ok) {
        try {
            const data = await response.json()
            error_display.textContent = data.detail
            console.log(JSON.stringify(data))
        }
        catch(error) {
            console.log(error)
            error_display.textContent = 'Server is down. try again later'
        }
        edit_form_submit_btn.disabled = false
        return
    }
    
    edit_form_submit_btn.disabled = false
    info_display.textContent = 'Successfully edited details'

    setTimeout(() => {
        info_display.textContent = ''
        edit_details_form.classList.add('hidden')
    }, 2000);
})