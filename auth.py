import models
from fastapi import HTTPException, status, Depends, Cookie
import jwt
from config import JWT_KEY
from logic.database import sql
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from logic.mails import send_email
import config
import secrets
from logic.database import sql
from typing import Annotated
import datetime as dt


security = HTTPBearer()

def get_current_user(access_token: Annotated[str | None, Cookie()] = None):
    if access_token is None:
        return
    try:
        data = jwt.decode(
            access_token,
            key = JWT_KEY,
            algorithms = ['HS256']
        )
    except jwt.ExpiredSignatureError as e:
        print(e)
        return
    except Exception as e:
        print(e)
        return

    ## must be access token
    if data.get('type') != 'access':
        print('Not access token')
        return
    
    # get user
    query = '''
        select * 
        from users
        where id = %s
    '''
    user_data = sql(query, [int(data['sub'])], fetch_all = False)
    return models.User(**user_data)


def send_email_verification_token(user: models.User):
    token = secrets.token_urlsafe()
    #xxxxxxxxxxxxxxxxxxxxxxXXXXXXXXXXXXX
    #   TODO: TOKEN EXIRATION
    #XXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXX
    query = '''
        update users
        set verification_token = %s
        where id = %s
    '''
    if sql(query, [token, user.id]) is None:
        return   

    # Send token to user
    verification_url = f'{config.DOMAIN_NAME}/auth/email/verify?user_id={user.id}&token={token}'
    text = f'R_TECH SOLUTIONS\n\n {verification_url}'
    send_email(
        {
            'body': text,
            'recipient': user.email,
            'subject': 'RTECH SOLUTIONS EMAIL VERIFICATION'
        }, 
        format = 'plain'   
    )
    return token
