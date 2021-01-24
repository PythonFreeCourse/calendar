from typing import List, Optional, Union
from fastapi import Depends, Form, Query
from pydantic import BaseModel, validator


class LoginUser(BaseModel):
    username: str
    hashed_password: str

    class Config:
        orm_mode = True
    


# class Jwt_User(Login_User):
#     is_active: Optional[bool] = False