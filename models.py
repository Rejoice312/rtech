from pydantic import BaseModel, EmailStr
from typing import Literal
import datetime as dt

def clean_fields(**args):
    for key, value in args.items():
        if isinstance(value, str):
            value = value.strip()
        elif isinstance(value, list):
            value = [
                value_element.strip() if isinstance(value_element, str) else value_element
                for value_element in value
            ]
#==============================
#   REQUEST MODELS
#==============================
class SubscribeRequest(BaseModel):
    email: EmailStr
    full_name: str
    courses: list[str]
    occupation: str
    goal: str
    country: str
    phone: str 


#===============================
#   RESPONSE MODELS
#===============================
class ErrorResponse(BaseModel):
    detail: str
    status: str = 'failed'

class BasicResponse(BaseModel):
    data: dict
    status: str = 'successful'

class SubscribeResponse(BasicResponse):
    data: SubscribeRequest



#==============================
#   OBJECT MODELS
#==============================
class Subscriber(SubscribeRequest):
    sub_timestamp: dt.datetime

class Job(BaseModel):
    job_description: str


#=========================
#       USERS
#=========================
class UpdateUser(BaseModel):
    full_name: str | None = None
    country: str | None = None
    resume: str | None = None
    linkedin: str | None = None
    portfolio: str | None = None
    application_email: str | None = None
    password: str | None = None

class BasicUser(BaseModel):
    full_name: str
    email: str
    country: str
    resume: str
    linkedin: str
    portfolio: str | None = None
    application_email: str | None = None

class UserResponse(BasicUser):
    id: int
    balance: float
    role: str = 'user'
    verified: bool = False

class SignupUser(BasicUser):
    password: str

class LoginUser(BaseModel):
    email: str
    password: str

class User(UserResponse):
    signup_timestamp: dt.datetime
    password_hash: str
