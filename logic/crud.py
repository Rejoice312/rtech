import re
from logic.database import sql
import datetime as dt




#================================
#   UTILS
#================================

# Get emails
def get_emails(table:str = 'subscribers'):
    query = f'select email from {table}'
    emails_dict_list = sql(query)
    if emails_dict_list is None:
        print('failed to fetch emails')
        return
    return [list(email_dict.values())[0] for  email_dict in emails_dict_list]  # convert to proper list



#================================
#   SUBSCRIBER MANAGEMENT
#================================

# Add subscriber
def add_subscriber(**sub_data):

    # strip string values
    for key, value in sub_data.items():
        if type(value) == str:
            sub_data[key] = value.strip()
        elif type(value) == list:
            sub_data[key] = [
                value_element.strip() if type(value_element) == str else value_element 
                for value_element in value
            ]

    ## invalid emails not allowed
    email_regex = re.compile(r'^[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Za-z]{2,}$')
    if email_regex.fullmatch(sub_data['email']) is None:
        print('Invalid Email')
        return

    ## required fields
    required_fields = [
        'full_name',
        'email',
        'courses',
        'occupation',
        'goal',
        'phone',
        'country'
    ]
  
    if not all([required_field in sub_data for required_field in required_fields]):
        print(f'All fields are required')
        return

    # format courses as pipe-seperated string
    sub_data['courses'] = ' | '.join(sub_data['courses'])

    # duplicate emails not allowed
    sub_emails = get_emails(table = 'subscribers')
    if sub_data['email'] in sub_emails:
        print('Email exists')
        return 

    # add the subscriber
    query = '''
    insert into subscribers(
        full_name, email, courses, occupation, goal, phone, country, sub_timestamp
    )
    values (
        %(full_name)s, %(email)s, %(courses)s, %(occupation)s, %(goal)s, %(phone)s,
        %(country)s, %(current_time)s
    )
    '''
    sub_data.update({'current_time': dt.datetime.now(dt.UTC)})
    if sql(query, params = sub_data):
        return 1

def get_subscribers(emails:list[str] | None = None):
    '''
    returns details for a list of subscribers
    or all subscribers if emails is None
    '''
    if emails is None:
        query = 'select * from subscribers'
    else:
        query = '''
            select * from subscribers 
            where email = any(%s)
        '''
    subscribers = sql(query, [emails])
    return subscribers



#======================
#   USER MANAGEMENT
#======================

def add_user(**user_data):
    pass