from typing import List, Optional, Union
from fastapi import Depends, Form, Query
from pydantic import BaseModel, validator



class LoginUser(BaseModel):
    '''
    Validating fields types
    Returns a User object for signing in.
    '''
    username: str
    hashed_password: str

    class Config:
        orm_mode = True
