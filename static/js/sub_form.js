const form = document.querySelector('form');
const errorDisplay = document.querySelector('.error')

form.addEventListener("submit", function (e) {
    errorDisplay.textContent = ''
    const checked = document.querySelectorAll(
        'input[name="courses"]:checked'
    );

    if (checked.length === 0) {
        e.preventDefault();
        errorDisplay.textContent = 'Select at least one course of interest'
    }
});