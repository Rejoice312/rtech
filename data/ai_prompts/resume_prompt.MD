# Context
You are an assistant to tailor **my resume** to the **job description** below
## My details
Full name: {full_name}
Country of Residence: {country}
Linkedin: {linkedin}
Portfolio: {portfolio}
Email: {application_email}
My resume: '''{resume}'''

## Job Description
'''{job_description}'''

## Resume Template
'''{resume_template}'''

# Requirements
* The resume structure should be this way 
  * strictly follow the structure provided in the **resume template** given
  * The first thing should be my name in header1
  * The contact info section appearing just after my name should contain my job titles and then my contact details
  * there must be two job titles included  in the contact info section: the first is the exact job title in the job description and the second is any  very closely related job title to that job title; if no job title can be found in the job description, default to 'Mechanical Engineer' and 'Data Analyst' respectively
  * After the contact info section, the resume should have only these sections: Education, Experience, Skills in exactly that order
  * My  Portfolio URL and LinkedIn URL should be hyperlinked to the texts: 'Porfolio' and 'LinkedIn' when being included in the contact info section. Do this only if made them available in **My Details** section above. skip anyone that is just blank or unavailable.
  * If the job is not a remote job, use the address in my resume as my address in the contact info section of the tailored resume.
  * If the job is a remote job, a physical address should not be included in the resume, just this 'GMT+1 Flexible to US and European timezones, Open to Remote Roles' should replace my address
* give me the resume as html text
* through out the resume, keywords included from the job description should be makde bold using the html b tag.

* For the Education section, do these:
  * Extract my education details (School and course of study) from my resume for inclusion in the tailored resume
  * If you cannot figure out my true education details from my resume, then just skip the education section entirely. Do not falsify details.
  * The date of education should not be included in the resume, neither the start nor end date should be included
  * Address of education should not be included

* For the experience section do these: 
  * Any of these can be considered an experience:
    * An experience stated in my resume
    * A project I did stated in my resume
    * An Internship stated in my resume
    * Projects stated in my portfolio
  * Choose 6 experiences according to the above rules for inclusion in my tailored resume
  * If I don't have up to 6 experiences meeting the criteria above in my original resume, generate more experriences resonating with the ones therein to make them up to 6.
  * The chosen experiences must be those most-relevant to the job description
  * For each experience, the job title should be made bold
  * For the first four experiences the job title should exactly match the job title in the job description if there is a job title in the job description
  * For each experience, there should be 3 bullet points
  * Each bullet point should be achievement-focused and results-oriented
  * Each bullet point should quantify achievements and results in percentages
  * For each bullet point, extract relevant keywords from the job description matching my  skills either directly or indirectly and find transferable ways to include those keywords in each bullet point
  * Each bullet point should be between 70  to 75 characters in length
  * Each bullet point must start on a new line
  * Dates should not be given to any experience that is just a project
  * For each experience, the job title should always appear before the project title
  * In each bullet point, when a keyword from the job description appears, it should be made bold
  * No experience should in anyway claim that I have worked for the company in the job description now before now
  * All 6 experiences should appear in decreasing order of relevance to the job job description
  * If a job title is not stated, research the company and figure out what kind of work they do and what roles they are most probably looking for and assume any two such related roles as the role for the job description

* For the skills section, do this:
  * Extract 10 skills from my resume and rewrite them in a transferrable way to the job description, using keywords from the job description when possible without lying

# Expectations
- your response should be only a json text with the following keys:
  - resume: the HTML text of the resume
  - job_title: the job title in the job description
  - organization: the name of the organization offering the job
- for each of the keys, if the job description does not include the value for the key, set it as null
- return only the json text without any explanations or surrounding texts
