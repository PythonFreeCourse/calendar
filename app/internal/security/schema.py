from typing import List, Optional

from app.database.models import UserEvent
from pydantic import BaseModel


class LoginUser(BaseModel):
    """
    Validating fields types
    Returns a User object for signing in.
    """
    username: str
    password: str

    class Config:
        orm_mode = True


class CurrentUser(BaseModel):
    """
    Security dependencies will return this object,
    instead of db object.
    Returns all User's parameters, except password.
    """
    id: int
    username: str
    full_name: str
    email: str
    language: str = None
    description: str = None
    avatar: str
    telegram_id: str = None
    events = Optional[List[UserEvent]]

    class Config:
        orm_mode = True
        arbitrary_types_allowed = True
