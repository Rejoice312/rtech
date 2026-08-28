let deposit_form = document.querySelector('#deposit-form')
let deposit_btn = document.querySelector('#deposit-btn')
let error_display = document.querySelector('.error')
let info_display = document.querySelector('.info')
let url


deposit_form.addEventListener('submit', async(event) => {
    event.preventDefault()
    let response
    let deposit_amount
    deposit_btn.disabled = true
    deposit_amount = document.querySelector('#deposit-amount').value 
    

    // try creating link
    info_display.textContent = 'Creating payment link...'
    try {
        response = await fetch(
            `/payments/url?amount=${deposit_amount}`,
            {
                method: 'GET', 
                headers: {'Content-Type': 'application/json'}
            }
        )
    }
    catch(error) {
        info_display.textContent = ''
        error_display.textContent = 'Failed to reach server. Try again'
        console.log(error)
    }
    info_display.textContent = ''

    if(!response.ok) {
        try {
            error_display.textContent = (await response.json()).detail
        }
        catch(error) {
            error_display.textContent = 'Failed to create payment link. Retry later'
            console.log(error)
        }
        deposit_btn.disabled = false
        return
    }

    url = (await response.json()).payment_url
    deposit_btn.disabled = false
    document.location.href = url
})