from logic.mails import read_mails, ai_reply
from typing import Literal
from logic.database import sql


def update_subscribers_field_from_mail(
        field: Literal['country', 'phone'],
        limit: int | None = None
    ):
    query = f'''
        select email
        from subscribers
        where {field} is null
        order by sub_timestamp desc
    '''
    if limit is not None:
        query = query + f'\nlimit {limit}'
    emails_without_field = sql(query, as_dict = False)
    # flatten
    emails_without_field = [
        email for email_tuple in emails_without_field
        for email in email_tuple
    ]

    # figure out field values from mail history
    with open(f'data/ai_prompts/get_{field}_prompt.MD', 'r') as f:
            prompt_template = f.read()
    data = []
    
    for email in emails_without_field:
        prior_conversations = read_mails(email, limit = 3)
        if prior_conversations is None:
            continue
        prompt = prompt_template.format(
            email = email,
            prior_conversations = prior_conversations
        )
        reply = ai_reply(prompt)
        if reply is None:
            continue
        if (field not in reply) or (reply.get(field, None) is None):
            continue

        query = f'''
            update subscribers
            set {field} = %s
            where email = '{email}'
        '''
        sql(query, params = [reply.get(field)])

        data.append(reply)

    return data


def follow_up_subscribers(limit: int):
     pass