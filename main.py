from fastapi import (
    FastAPI, 
    Form, 
    status, 
    HTTPException,
    Request,
    Depends,
    BackgroundTasks,
    Response,
)
from fastapi.responses import RedirectResponse
from typing import Annotated
import models
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from data import data
from logic import crud
from logic import mails
from contextlib import asynccontextmanager
from apscheduler.schedulers.asyncio import AsyncIOScheduler
import cron_jobs
from pwdlib import PasswordHash
import datetime as dt
from logic.database import sql, get_con
import config
import jwt
import auth
from logic.resume_generator import generate_resume
import requests
import hmac
import pandas as pd
import re


password_hasher = PasswordHash.recommended()
RESUME_COST = 0.3   # resume cost in dollars
MINIMUM_DEPOSIT = 10 # in dollars
INITIAL_USER_BALANCE = 1
PASSWORD_REGEX = re.compile(r'^(?=.*[A-Z])(?=.*[a-z])(?=.*\d)(?=.*[^A-Za-z0-9]).+$')

#================
#   CRON JOBS
#================

scheduler = AsyncIOScheduler()

@asynccontextmanager
async def lifespan(app: FastAPI):
    scheduler.add_job(
        cron_jobs.update_subscribers_field_from_mail, 
        'cron', 
        day_of_week = 'mon',
        hour = 8,
        timezone = 'UTC',
        args = ['country']
    )
    scheduler.start()

    yield

    scheduler.shutdown()


app = FastAPI(
    docs_url="/docs" if config.DEBUG else None,
    redoc_url="/redoc" if config.DEBUG else None,
    openapi_url="/openapi.json" if config.DEBUG else None,
    lifespan = lifespan
)

app.mount(
    '/static',
    StaticFiles(directory = 'static'),
    name = 'static'
)

templates = Jinja2Templates(directory = 'templates')

 
#==========================
#   SUBSCRIBER MANAGEMENT
#==========================

# Subscriber form
@app.get('/forms/subscribe')
def subscriber_form(request: Request):
    return templates.TemplateResponse(
        request = request,
        name = 'sub_form.html',
        context = {
            'courses': data.COURSES,
            'countries': sorted(data.COUNTRIES)
        }
    )



#========================
#   PAGES
#========================

# home page
@app.get('/', name = 'home')
async def home(request: Request):
    return templates.TemplateResponse(
        request = request,
        name = 'home.html',
        context = {
            'courses': data.COURSES
        }
    )
#

# Signup form 
@app.get('/pages/signup')
def signup_form(request: Request):
    return templates.TemplateResponse(
        request = request,
        name = 'signup.html',
        context = {
            'countries': sorted(data.COUNTRIES)
        }
    )


# Login form 
@app.get('/pages/login')
def login_form(request: Request):
    return templates.TemplateResponse(
        request = request,
        name = 'login.html'
    )


# Dashboard page
@app.get('/pages/dashboard')
def show_dashboard(request: Request, user: models.User = Depends(auth.get_current_user)):
    if user is None:
        return RedirectResponse('/pages/login')

    query = '''
        select *
        from applications 
        where user_id = %s 
        order by application_timestamp desc
        limit 30
    '''
    applications = sql(
        query,
        [user.id],
        fetch_all = True
    )
    applications = pd.DataFrame(applications)
    applications['application_timestamp'] = applications.application_timestamp.dt.date
    applications['job_description'] = applications.job_description.map(
        lambda desc: desc[:50].strip() + '...' if desc.strip() else pd.NA
    )
    applications = applications.fillna('N/A').to_dict(orient = 'records')
    return templates.TemplateResponse(
        request = request,
        name = 'dashboard.html',
        context = {
            'user': user.model_dump(),
            'applications': applications
        }
    )


# Resume page
@app.get('/pages/resume')
def show_resume_page(request: Request, user: models.User = Depends(auth.get_current_user)):
    if user is None:
        return RedirectResponse('/pages/login')
    return templates.TemplateResponse(
        request = request,
        name = 'resume.html',
        context = {
            'user': user.model_dump()
        }
    )


@app.get('/pages/profile')
def show_profile(request: Request, user: models.User = Depends(auth.get_current_user)):
    if user is None:
        return RedirectResponse('/pages/login')
    return templates.TemplateResponse(
        request = request,
        name = 'profile.html',
        context = {
            'user': user.model_dump(),
            'countries': sorted(data.COUNTRIES)
        }
    )


# Add subscriber
@app.post('/forms/subscribe')
async def add_subscriber(
    request: Request,
    subscriber: Annotated[models.SubscribeRequest, Form()],
    background_tasks: BackgroundTasks
):
    if not crud.add_subscriber(**subscriber.model_dump()):
        raise HTTPException(
            status_code = status.HTTP_422_UNPROCESSABLE_CONTENT,
            detail = 'Invalid data, or subscriber exists'
        )

    # send initial email asynchronously
    background_tasks.add_task(mails.create_and_send_mail, subscriber.email)
    # return success page
    return templates.TemplateResponse(
        request = request,
        name = 'subscription_success.html',
        context = subscriber.model_dump()
    )



#=======================
#   AUTHENTICATION
#======================
@app.post('/auth/signup', response_model=models.BasicUser)
def sign_up(signup_user: models.SignupUser, response: Response):
    # data validation
    ## strip string fields and ensure right case
    lowercase_fields = [
        'email',
        'linkedin',
        'portfolio'
    ]
    title_case_fields = [
        'full_name', 
        'country', 

    ]

    for field, value in signup_user:
        if value is not None:
            value = value.strip()
            if field in lowercase_fields:
                value = value.lower()
            if field in title_case_fields:
                value = value.title()
            setattr(signup_user, field, value)

        
    ## required fields dont allow empty strings
    required_fields = [
        'full_name',
        'email',
        'country',
        'password_hash',
        'resume',
        'linkedin',
    ]

    if not all([
        value for _, value in signup_user
        if value in required_fields
    ]):
        raise HTTPException(
            status_code = status.HTTP_400_BAD_REQUEST,
            detail = 'Invalid data'
        )
    
    ## Name shouldn't be too long
    if len(signup_user.full_name) > 40:
        raise HTTPException(
            status_code = status.HTTP_422_UNPROCESSABLE_CONTENT,
            detail = 'Name is too long!'
        )

    ## Resume length limits
    signup_user.resume = re.sub(r'\s+', ' ', signup_user.resume) # first remove excess spaces
    if not (1000 < len(signup_user.resume) < 6933):
        raise HTTPException(
            status_code = status.HTTP_422_UNPROCESSABLE_CONTENT,
            detail = 'Resume is too long or too short'
        )

    ## password within char limit
    if not (8 <= len(signup_user.password) <= 20):
        raise HTTPException(
            status_code = status.HTTP_422_UNPROCESSABLE_CONTENT,
            detail = 'Password must be betweeen 8 and 20 characters'
        )
    
    ## password must be secure: includes each of
    ## capital, lower case, number and special char
    if PASSWORD_REGEX.fullmatch(signup_user.password) is None:
        raise HTTPException(
            status_code = status.HTTP_422_UNPROCESSABLE_CONTENT,
            detail = 'Password must contain an upper case, lower case, numeric and special character'
        )


    ## No duplicate emails
    query = '''
        select %s in (
            select email
            from users
        )
    '''
    res = sql(query, [signup_user.email], as_dict = False, fetch_all = False)
    if res is None:
        raise HTTPException (
            status_code = status.HTTP_502_BAD_GATEWAY,
            detail = 'Failed to sign up. Try again later'
        )
    user_exists = res[0]
    if user_exists:
        raise HTTPException(
            status_code = status.HTTP_400_BAD_REQUEST,
            detail = 'User exists'
        )   

    # default application email to user email
    signup_user.application_email = signup_user.email

    user_data = {
        **signup_user.model_dump(),
        **{
            'password_hash': password_hasher.hash(signup_user.password),
            'signup_timestamp': dt.datetime.now(dt.UTC),
            'balance': INITIAL_USER_BALANCE
        }
    }
    
    # add user, returning the user
    query = '''
        insert into users(
            full_name, email, country, password_hash, signup_timestamp, 
            balance, resume, linkedin, portfolio, application_email
        )
        values(
            %(full_name)s, %(email)s, %(country)s, %(password_hash)s,
            %(signup_timestamp)s, %(balance)s, %(resume)s, %(linkedin)s, 
            %(portfolio)s, %(application_email)s
        )
        returning *
    '''
    user_data = sql(query, user_data)
    if user_data is None:
        raise HTTPException(
            status_code = status.HTTP_502_BAD_GATEWAY,
            detail = 'Server is down. Try again later 1'
        )
    user = models.User(**user_data)

    # set access_token
    access_token = jwt.encode(
        payload = {
            'sub': str(user.id),
            'exp': dt.datetime.now(dt.UTC) + dt.timedelta(hours = 3),
            'iat': dt.datetime.now(dt.UTC),
            'type': 'access'
        },
        key = config.JWT_KEY,
        algorithm = 'HS256'
    )
    response.set_cookie(
        key = 'access_token',
        value = access_token,
        path = '/',
        httponly = False if config.DEBUG else True,
        secure = False if config.DEBUG else True
    )

    # try sending email verification token and updating user table
    try:
        token = auth.send_email_verification_token(user)
        query = '''
            update users
            set verification_token = %s
            where id = %s
        '''
        sql(query, [token, user.id])
    except:
        pass
    
    return user


# send email verification token
@app.get('/auth/email_token')
def send_email_verification_token(user: models.User = Depends(auth.get_current_user)):
    if user is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail='Session expired'
        )
    # confirm user not verified
    query = '''
        select verified
        from users
        where id = %s
    '''
    res = sql(query, [user.id], as_dict = False, fetch_all = False)
    if res is None:
        raise HTTPException(
            status_code = status.HTTP_502_BAD_GATEWAY,
            detail = 'Failed to verify user'
        )
    is_verified = res[0]
    if is_verified:
        raise HTTPException(
            status_code = status.HTTP_400_BAD_REQUEST,
            detail = 'User already verified'
        )
    # try sending the token
    if not auth.send_email_verification_token(user):
        raise HTTPException(
            status_code = status.HTTP_502_BAD_GATEWAY,
            detail = 'Failed to send verification token'
        )
    return {'status': 'success'}

         

# Verify signup email
@app.get('/auth/email/verify')
def verify_email(user_id: int, token: str):

    # verify token
    query = '''
        select verification_token
        from users
        where id = %s
    '''
    res = sql(query, [user_id], fetch_all = False)
    if res is None:
        raise HTTPException(
            status_code = status.HTTP_401_UNAUTHORIZED,
            detail = 'Invalid token'
        )

    db_token = res['verification_token']
    print(db_token)
    if token != db_token:
        raise HTTPException(
            status_code = status.HTTP_401_UNAUTHORIZED,
            detail = 'Invalid token'
        )

    # mark user as verified
    query = '''
        update users 
        set verified = true
        where id = %s
    '''
    if sql(query, [user_id]) is None:
        raise HTTPException(
            status_code = status.HTTP_502_BAD_GATEWAY,
            detail = 'Verification failed'
        )
    return {'status': 'successful'}


@app.post('/auth/login')
def login(login_user: models.LoginUser, response: Response):
    # verify email
    query = 'select * from users where email = %s'
    user_data = sql(query, [login_user.email.lower().strip()], fetch_all = False)
    if user_data is None:
        raise HTTPException(
            status_code = status.HTTP_401_UNAUTHORIZED,
            detail = 'User does not exist'
        )
    user = models.User(**user_data)

    # verify password
    if not password_hasher.verify(login_user.password.strip(), user.password_hash):
        raise HTTPException(
            status_code = status.HTTP_401_UNAUTHORIZED,
            detail = 'Incorrect Password'
        )

    # create JWT refresh and access token
    access_payload = {
        'sub': str(user.id),
        'type': 'access',
        'iat': dt.datetime.now(dt.UTC),
        'exp': dt.datetime.now(dt.UTC) + dt.timedelta(hours=3)
    }

    access_token = jwt.encode(
        access_payload,
        key = config.JWT_KEY,
        algorithm = 'HS256'
    )

    # response cookies: refresh token and session_id
    response.set_cookie(
        key = 'access_token',
        value = access_token,
        path = '/',
        httponly = True if config.DEBUG else False,
        secure = True if config.DEBUG else False
    )

    return {
        'access_token': access_token,
        'type': 'bearer'
    }


# Log out
@app.get('/auth/logout')
def logout(response: Response):
    response = RedirectResponse('/pages/login')
    response.delete_cookie('access_token')
    return response


#===================
#   USERS
#===================

@app.patch('/users/me/edit')
def edit_user(update_user: models.UpdateUser, user: models.User = Depends(auth.get_current_user)):
    if user is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail = 'Session expired. Re-login'
        )
    # validations
    lowercase_fields = [
            'email',
            'linkedin',
            'portfolio'
        ]
    title_case_fields = [
        'full_name', 
        'country', 

    ]
    for field, value in update_user:
        if value is not None:
            if field in lowercase_fields:
                value = value.lower()
            if field in title_case_fields:
                value = value.title()
            setattr(update_user, field, value.strip())

    # remove unncessary resume spaces
    if update_user.resume:
        update_user.resume = re.sub(r'\s+', ' ', update_user.resume)

    error_conditions = [
        (update_user.full_name) and (len(update_user.full_name) > 40),
        (update_user.country) and (update_user.country not in data.COUNTRIES),
        (update_user.resume) and (not(1000 < len(update_user.resume) < 6933)),
        (update_user.password) and (not PASSWORD_REGEX.fullmatch(update_user.password)),
        (update_user.password) and (len(update_user.password) < 8)
    ]

    error_messages = [
        'Name too long',
        'Invalid country',
        'Resume too long or too short',
        'Password must contain each of a digit, lower case, upper case and special character',
        'Password must be at least characters long'
    ]

    for error_condition, error_message in zip(error_conditions, error_messages):
        if error_condition:
            print(update_user)
            raise HTTPException(
                status_code = status.HTTP_422_UNPROCESSABLE_CONTENT,
                detail = error_message
            )

    # Update user details
    query = 'update users set'
    for field, value in update_user:
        if value:
            query += f'\n{field} = %s\n'

    if sql(query, [value for _, value in update_user if value]) is None:
        raise HTTPException(
            status_code = status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail = 'Failed to update details'
        )
    return {'status': 'success'}



#=======================
#   PAYMENTS
#======================
@app.get('/payments/url')
def get_payment_url(
    amount: float,
    user: models.User = Depends(auth.get_current_user)
):
    if user is None:
        raise HTTPException(
            status_code = status.HTTP_401_UNAUTHORIZED,
            detail = 'Session expired'
        )
    # amount greater than threshold
    if amount < MINIMUM_DEPOSIT:
        raise HTTPException(
            status_code = status.HTTP_400_BAD_REQUEST,
            detail = 'Amount too small'
        )
    url = 'https://api.flutterwave.com/v3/payments'
    txn_ref = f'pay_{user.id}_{dt.datetime.now(dt.UTC).timestamp()}'
    payload = {
        'tx_ref': txn_ref,
        'amount': amount,
        'currency': 'USD',
        'redirect_url': f'{config.DOMAIN_NAME}/pages/dashboard',
        'customer': {
            'email': user.email,
            'id': user.id,
        },
        'customizations': {
            'title': 'R-Tech Solutions',
            'description': 'Account top up'  
        }
    }

    headers = {
        'Authorization': f'Bearer {config.FLW_SECRET_KEY}',
        'Content-Type': 'application/json'
    }
    try:
        response = requests.post(
            url,
            json = payload,
            headers = headers
        )
    except (requests.ConnectionError, requests.ConnectTimeout):
        raise HTTPException(
            status_code=status.HTTP_504_GATEWAY_TIMEOUT,
            detail='Connection error, try again later'
        )
    except Exception as e:
        print(e)
        raise HTTPException(
            status_code = status.HTTP_502_BAD_GATEWAY,
            detail = 'Some error occured. Try again later'
        )
    if response.status_code != status.HTTP_200_OK:
        raise HTTPException(
            status_code = status.HTTP_502_BAD_GATEWAY,
            detail = 'Unable to get payment link, try again'
        )

    # create pending transaction
    query = '''
        insert into txns(
            txn_ref, amount, user_id, status, 
            type, description, txn_timestamp
        )
        values(
            %(txn_ref)s, %(amount)s, %(user_id)s, %(status)s,
            %(type)s, %(description)s, %(txn_timestamp)s
        )
    '''
    if not sql(
        query,
        params = {
            'txn_ref': txn_ref,
            'amount': amount,
            'status': 'pending',
            'user_id': user.id,
            'type': 'credit',
            'description': 'Deposit',
            'txn_timestamp': dt.datetime.now(dt.UTC)
        }
    ):
        raise HTTPException(
            status_code = status.HTTP_502_BAD_GATEWAY,
            detail = 'Failed to initiate transaction. Try again later'
        )
    payment_url = response.json()['data']['link']
    return {'payment_url': payment_url}


@app.post('/payments/webhook')
async def verify_payment(request: Request):
    # verify data from payment platform
    signature = request.headers.get('verif-hash')
    if not signature:
        raise HTTPException(
            status_code = 401,
            detail = 'Missing webhook signature'
        )

    if not hmac.compare_digest(signature, config.FLW_SECRET_HASH):
        raise HTTPException(
            status_code = 401,
            detail = 'Invalid webhook signature'
        )

    # update txn and update user balance simultaneously
    data = await request.json()
    status = 'successful' if data.get('status') == 'successful' else 'failed'
    con = get_con()
    cursor = con.cursor()
    query = '''
        update txns
        set status = %s
        where txn_ref = %s
    '''
    try:
        cursor.execute(query, [status, data.get('txRef')])
    except:
        print('Transaction record failed: ', data)
        con.rollback()

    query = '''
        update users
        set balance = balance + %s
        where id = (
            select user_id
            from txns
            where txn_ref = %s
        )
    '''
    try:
        cursor.execute(query, [data.get('amount'), data.get('txRef')])
        print('Payment Recieved')
    except:
        print('Balance update failed: ', data)
        con.rollback()
    finally:
        con.commit()
        cursor.close()
        con.close()



#=====================
#   RESUME CREATOR
#=====================

@app.post('/resumes/create')
async def create_resume(
    job: models.Job,
    user: models.User = Depends(auth.get_current_user)
):
    if user is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail = 'Session Expired. Re-login'
        )
    # verify user balance
    if (user.balance < RESUME_COST) and (user.role not in ['admin']):
        raise HTTPException(
            status_code = status.HTTP_402_PAYMENT_REQUIRED,
            detail = 'Insufficient balance'
        )

    # generate resume
    resume_res = generate_resume(user, job.job_description)
    if resume_res is None:
        raise HTTPException(
            status_code = status.HTTP_504_GATEWAY_TIMEOUT,
            detail = 'Resume generation failed'
        )

    # record application
    query = '''
        select count(*)
        from applications
        where user_id = %s
    '''
    response = sql(query, [user.id], as_dict = False)
    resume_number = response[0] if response else 0
    resume_file_name = f'{user.full_name}_{user.id}_{resume_number}.pdf'
    query = '''
        insert into applications(
            job_title, organization, job_description,
            application_timestamp, user_id, resume
        )
        values (
            %(job_title)s, %(organization)s, %(job_description)s,
            %(application_timestamp)s, %(user_id)s, %(resume)s
        )
    '''
    params = {
        'job_description': job.job_description,
        'application_timestamp': dt.datetime.now(dt.UTC),
        'user_id': user.id,
        'resume': resume_file_name,
        'job_title': resume_res.get('job_title'),
        'organization': resume_res.get('organization')
    }
    sql(query, params)  # even if the record fails, we proceed
    
    # add debit transaction and update balance simultaneously
    if user.role not in ['admin']:
        con = get_con()
        cursor = con.cursor()
        query = '''
            insert into txns(
                txn_ref, amount, user_id,
                type, description, txn_timestamp, status
            )
            values(
                %(txn_ref)s, %(amount)s, %(user_id)s,
                %(type)s, %(description)s, %(txn_timestamp)s, %(status)s
            )
        '''
        try:
            cursor.execute(
                query,
                params = {
                    'txn_ref': f'resume_{user.id}_{dt.datetime.now(dt.UTC).timestamp()}',
                    'amount': RESUME_COST,
                    'user_id': user.id,
                    'type': 'debit',
                    'description': 'Resume creation',
                    'txn_timestamp': dt.datetime.now(dt.UTC),
                    'status': 'successful'
                }
            )
        except:
            con.rollback()
            raise HTTPException(
                status_code = status.HTTP_502_BAD_GATEWAY,
                detail = 'Transaction failed. Try again'
            )

        query = '''
            update users
            set balance = balance - %s
            where id = %s
        '''
        try:
            cursor.execute(query, [RESUME_COST, user.id])
            con.commit()
        except:
            con.rollback()
            raise HTTPException(
                status_code = status.HTTP_502_BAD_GATEWAY,
                detail = 'Transaction failed. Try again'
            )
        finally:
            cursor.close()
            con.close()

    # send resume 
    return Response(
        content = resume_res['resume'],
        media_type = 'application/pdf',
        headers = {
            'Content-Disposition': f'inline; filename={resume_file_name}'
        }
    )
    