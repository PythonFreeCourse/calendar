from app.database.models import Note
from app.database.schemas import NoteSchema
from app.internal.utils import create_model
from sqlalchemy.orm.session import Session


async def post(session: Session, payload: NoteSchema):
    note = create_model(session, Note, title=payload.title, description=payload.description)
    return note.id
