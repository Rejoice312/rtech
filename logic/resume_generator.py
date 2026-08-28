import models
from logic.ai import ai_reply
import datetime as dt
from weasyprint import HTML
from logic.database import sql


def generate_resume(user: models.User, job_description: str):
    '''
    creates a tailored resume to job description
    using users resume, return a bytes object in memory
    without saving to disk, keeping records of job applications

    returns a dictionary of keys:
    resume: the pdf resume as bytes
    job_title: the job title in job description
    organization: the organization offering the job
    '''

    # get html resume and job details in a dictionary with AI
    with open('data/ai_prompts/resume_prompt.MD') as f:
        prompt_template = f.read()
    with open('data/resume_template.html') as f:
        resume_template = f.read()

    prompt = prompt_template.format(
        job_description = job_description,
        resume_template = resume_template,
        **user.model_dump()
    )
    response = ai_reply(prompt, as_dict = True)

    ## resume must exist
    if ('resume' not in response) or (response['resume'] is None) or (not response['resume'].strip()):    
        return 

    # send resume as pdf
    resume = HTML(string = response['resume']).write_pdf()
    response['resume'] = resume
    return response