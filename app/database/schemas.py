from datetime import date
from pydantic import BaseModel


class Event(Base):
    id: int
    title: str
    start: date
    end: date
    vc_link: str
    content: str
    location: str
    owner_id: int
    color: str

    class Config:
        orm_mode = True
