from app.database.models import Note
from app.database.schemas import NoteSchema
from sqlalchemy.orm import Session


async def post(session: Session, payload: NoteSchema):
    note = Note(title=payload.title, description=payload.description)
    session.add(note)
    session.commit()
    session.refresh(note)
    return note.id


async def get(session: Session, id: int):
    return session.query(Note).filter_by(id=id).first()
