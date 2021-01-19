import re
from typing import List
from fastapi import Depends, Form, Query
from pydantic import BaseModel, validator, EmailStr, EmailError


def form_body(cls):
    cls.__signature__ = cls.__signature__.replace(
        parameters=[
            arg.replace(default=Form(...))
            for arg in cls.__signature__.parameters.values()
        ]
    )
    return cls

@form_body
class UserBase(BaseModel):
    username: str
    email: str 
    first_name: str
    last_name: str
        
@form_body
class UserCreate(UserBase):
    password: str
    confirm_password: str

    @validator('confirm_password')
    def passwords_match(cls, confirm_password, values, **kwargs):
        if 'password' in values and confirm_password != values['password']:
            return {"message": "Passwords don't match"}
        return confirm_password
  
    @validator('username')
    def username_length(cls, username):
        if username == "":
            return {"message": "Username field can not be empty"}
        if len(username) < 3:
            return {"message": "Username must contain minimum of 3 characters"}
        return username
    
    @validator('email')
    def confirm_mail(cls, email):
        try:
            EmailStr.validate(email)
            return email
        except EmailError:
            return {"message": "Email address is not valid"}


class User(UserBase):
    id: int
    is_active: bool
    events: List[int] = []

    class Config:
        orm_mode = True
