from datetime import datetime
from typing import Any, Dict, List

from fastapi import HTTPException, status
from sqlalchemy.orm import Session

from app.database.models import Note
from app.database.schemas import NoteSchema


async def create(session: Session, payload: NoteSchema) -> int:
    note = Note(
        title=payload.title,
        description=payload.description,
        creator=payload.creator,
    )
    session.add(note)
    session.commit()
    session.refresh(note)
    return note.id


async def view(session: Session, note_id: int) -> Note:
    note = session.query(Note).filter_by(id=note_id).first()
    if not note:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Note with id {note_id} not found",
        )
    return note


async def get_all(
    session: Session,
    skip: int = 0,
    limit: int = 100,
) -> List[Note]:
    return session.query(Note).offset(skip).limit(limit).all()


async def update(request: NoteSchema, session: Session, note_id: int) -> str:
    note = session.query(Note).filter_by(id=note_id)
    if not note.first():
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Note with id {note_id} not found",
        )
    if request.timestamp is None:
        request.timestamp = datetime.utcnow()
    note.update(request.dict(exclude_unset=True), synchronize_session=False)
    session.commit()
    return "updated"


async def delete(session: Session, note_id: int) -> str:
    note = session.query(Note).filter_by(id=note_id)
    if not note.first():
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Note with id {note_id} not found",
        )
    note.delete(synchronize_session=False)
    session.commit()
    return "deleted"


async def create_note(note: NoteSchema, session: Session) -> Dict[str, Any]:
    note_id = await create(session, note)
    return {"id": note_id, **dict(note)}
