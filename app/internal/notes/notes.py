from datetime import datetime
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


async def get_all(session: Session, skip: int = 0, limit: int = 100):
    return session.query(Note).offset(skip).limit(limit).all()


async def put(session: Session, id: int, payload: NoteSchema):
    note = session.query(Note).filter_by(id=id).first()
    note.title = payload.title
    note.description = payload.description
    note.timestamp = datetime.utcnow
    session.commit()
    session.refresh(note)
    return note


async def delete(session: Session, id: int):
    note = session.query(Note).filter_by(id=id).first()
    session.query(Note).filter_by(id=id).delete()
    session.commit()
    return note
