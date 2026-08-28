from logic.google.gmail import Gmail
from typing import Literal
from logic import crud
from logic.ai import ai_reply
import config


try:
    gmail = Gmail()
except Exception as e:
    if config.DEBUG:
        print(e)
    else:
        raise e


def read_mails(email: str, limit: int = 3):     
    try:
        return gmail.read(email)[:limit]
    except Exception as e:
        print(f'failed to read mail history {e}')
        return 


def create_mail(email: str):
    subscriber_data = crud.get_subscribers([email])
    if not subscriber_data:
        print('Failed to retrieve subscriber\'s')
        return 
    subscriber_data = subscriber_data[0]

    with open('data/ai_prompts/email_prompt.MD') as f:
        prompt_template = f.read()

    try:
        prior_conversations = read_mails(email, limit = 3)
    except Exception as e:
        print(f'failed to read mail history {e}')
        return 

    subscriber_data.update({'prior_conversations': prior_conversations})
    prompt = prompt_template.format(**subscriber_data)

    mail = ai_reply(prompt)
    if mail is None:
        print(f'Failed to create mail for {email}')
        return
        
    if not all(
        [
            'body' in mail,         # body must be present
            'subject' in mail,      # subject must be present
            'stage' in mail,
            mail.get('body'),       # body must have a value
            mail.get('subject'),     # subject must have a value
            mail.get('stage')
        ]
    ):
        print(f'Invalid mail generated for {email}')
        return 
    try:
        mail['stage'] = int(mail['stage'])
    except:
        print(f'Invalid mail generated for {email}')
        return 
    return mail


def send_email(mail: dict, format: Literal['html', 'plain'] = 'html'):
    # data validation
    required = ['recipient', 'subject', 'body']
    incomplete_keys = not all([key in mail for key in required])
    incomplete_values = any([value is None for value in mail.values() if value in required])
    if incomplete_keys or incomplete_values:
        print('Invalid mail')
        return 
    
    try:
        gmail.send(
            body = mail.get('body'),
            recipient = mail.get('recipient'),
            subject = mail.get('subject'),
            format = format
        )
    except:
        print(f'Failed to send mail to {mail['recipient']}')
        return
    return 1


def create_and_send_mail(email):
    print(f'Creating mail for {email}')
    mail = create_mail(email)
    if mail is None:
        return
    
    print(f'Sending mail to {email}')
    mail.update({'recipient': email})
    if  not send_email(mail):
        return
    print(f'Sent mail to {email}')