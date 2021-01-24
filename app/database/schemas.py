from datetime import date
from pydantic import BaseModel

   
class User(BaseModel):
   
    id: str
    username: str
    email: str
    password: str
    is_active: bool

    class Config:
            orm_mode = True

class Event(Base):
    id: int
    title: str
    start_date: date
    end_date: date
    vc_link: str
    content: str
    location: str
    owner_id: int

        class Config:
            orm_mode = True
