from pydantic import BaseModel, HttpUrl # pylint: disable-msg=E0611
from datetime import datetime

class EventBasic(BaseModel):
    id: int
    title: str
    start_date: datetime
    end_date: datetime
    VC_link: HttpUrl
    content: str
    location: str
    owner_id: int

