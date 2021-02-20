from datetime import datetime
from typing import Any, Dict, List

from app.database.models import Note
from app.database.schemas import NoteSchema
from fastapi import HTTPException, status
from sqlalchemy.orm import Session


async def create(session: Session, payload: NoteSchema) -> int:
    note = Note(title=payload.title, description=payload.description)
    session.add(note)
    session.commit()
    session.refresh(note)
    return note.id


async def view(session: Session, id: int) -> Note:
    note = session.query(Note).filter_by(id=id).first()
    if not note:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Note with id {id} not found",
        )
    return note


async def get_all(
    session: Session, skip: int = 0, limit: int = 100
) -> List[Note]:
    return session.query(Note).offset(skip).limit(limit).all()


async def update(request: NoteSchema, session: Session, id: int) -> str:
    note = session.query(Note).filter_by(id=id)
    if not note.first():
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Note with id {id} not found",
        )
    if request.timestamp is None:
        request.timestamp = datetime.utcnow()
    note.update(request)
    session.commit()
    return "updated"


async def delete(session: Session, id: int) -> str:
    note = session.query(Note).filter_by(id=id)
    if not note.first():
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Note with id {id} not found",
        )
    note.delete(synchronize_session=False)
    session.commit()
    return "deleted"


async def create_note(note: NoteSchema, session: Session) -> Dict[str, Any]:
    note_id = await create(session, note)
    response_object = {
        "id": note_id,
        "title": note.title,
        "description": note.description,
        "timestamp": note.timestamp,
    }
    return response_object
