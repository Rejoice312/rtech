let resume_form = document.querySelector('#resume-form')
let error_display = document.querySelector('.error')
let info_display = document.querySelector('.info')
let response
let job_description
let resume
let resume_submit_btn = document.querySelector('#resume-form button')

resume_form.addEventListener('submit', async (event) => {
    event.preventDefault()
    resume_submit_btn.disabled = true
    error_display.textContent = ''
    info_display.textContent = ''

    // read job description
    job_description = document.querySelector('#job-description').value
    // get resume

    info_display.textContent = 'Generating resume...'
    response = await fetch(
        '/resumes/create',
        {
            method: 'POST',
            body: JSON.stringify({
                job_description: job_description
            }),
            headers: {
                'Content-type': 'application/json'
            }
        }
    )
    
    info_display.textContent = ''

    // failed response? show error
    if(!response.ok) {
        console.log(response)
        try{
            error_display.textContent = (await response.json()).detail
        }
        catch(error) {
            console.log(error)
            error_display.textContent = 'Failed to Create resume'
        }
        
        resume_submit_btn.disabled = false
        return
    }

    const resume = await response.blob()

    if(!resume) {
        error_display.textContent = 'Failed to Generate resume'
        resume_submit_btn.disabled = false
        return
    }
    info_display.textContent = 'Resume generated'

    // 1. Extract the filename from Content-Disposition header
    const disposition = response.headers.get('Content-Disposition');
    let filename = 'resume.pdf'; // Fallback filename

    if (disposition && disposition.includes('filename=')) {
        const match = disposition.match(/filename="?([^"]+)"?/);
        if (match && match[1]) {
            filename = match[1];
        }
    }

    // 2. Convert response stream to a Blob
    const url = URL.createObjectURL(resume);

    // 3. Create a temporary <a> tag to trigger the download
    const a = document.createElement('a');
    a.href = url;
    a.download = filename;
    document.body.appendChild(a);
    a.click();

    // 4. Cleanup resources
    a.remove();
    URL.revokeObjectURL(url);
    resume_submit_btn.disabled = false;
})