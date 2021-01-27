from fastapi_users import models
from pydantic import validator
from typing import Optional

class User(models.BaseUser):
    username: str
    full_name:str
    description: Optional[str] = None
    avatar: Optional[str] = None

class UserCreate(models.BaseUserCreate):
    username: str
    full_name:str
    description: Optional[str] = None
    avatar: Optional[str] = None

    @validator('password')
    def valid_password(cls, v: str):
        if len(v) < 6:
            raise ValueError('Password should be at least 6 characters')
        return v


class UserUpdate(User, models.BaseUserUpdate):
    pass


class UserDB(User, models.BaseUserDB):
    pass