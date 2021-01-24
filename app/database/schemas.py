from typing import List, Optional
from datetime import datetime
from pydantic import BaseModel


class EventBase(BaseModel):
    title: str
    content: Optional[str] = None


class EventCreate(EventBase):
    pass


class Event(EventBase):
    id: int
    owner_id: int

    class Config:
        orm_mode = True


class UserBase(BaseModel):
    username: str
    email: str


class UserCreate(UserBase):
    password: str


class User(UserBase):
    id: int
    is_active: bool
    events: List[Event] = []

    class Config:
        orm_mode = True