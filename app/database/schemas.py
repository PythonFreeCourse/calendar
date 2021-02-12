from datetime import datetime
from typing import Optional
from pydantic import BaseModel


class NoteSchema(BaseModel):
    title: str
    description: Optional[str] = None
    timestamp: Optional[datetime]

    class Config:
        orm_mode = True
        schema_extra = {
            "example": {
                "title": "Foo",
                "description": "Bar",
            }
        }


class NoteDB(NoteSchema):
    id: int
