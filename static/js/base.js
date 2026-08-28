body = document.querySelector('body')
mode_btn = document.querySelector('#mode-btn')
saved_mode = localStorage.getItem('mode')


// read saved mode
if(saved_mode == 'light') {
    mode_btn.textContent = 'Dark mode'
    body.classList.remove('dark-mode')
}
else {
    // default to dark mode
    mode_btn.textContent = 'Light mode'
    body.classList.add('dark-mode')
}

// changing dark and light mode
mode_btn.addEventListener('click', () => {
    if(mode_btn.textContent == 'Light mode') {
        mode_btn.textContent = 'Dark mode'
        body.classList.remove('dark-mode')
        localStorage.setItem('mode', 'light')
    }
    else {
        mode_btn.textContent = 'Light mode'
        body.classList.add('dark-mode')
        localStorage.setItem('mode', 'dark')
    }
})

