from app.database.schemas import NoteDB, NoteSchema
from app.dependencies import get_db
from app.internal.notes import notes
from fastapi import APIRouter
from fastapi import HTTPException
from fastapi.param_functions import Depends
from sqlalchemy.orm import Session
from typing import List


router = APIRouter(
    prefix="/notes",
    tags=["notes"],
    responses={404: {"description": "Not found"}},
)


@router.post("/", response_model=NoteDB, status_code=201)
async def create_note(payload: NoteSchema, session: Session = Depends(get_db)):
    note_id = await notes.post(session, payload)

    response_object = {
        "id": note_id,
        "title": payload.title,
        "description": payload.description,
        "timestamp": payload.timestamp
    }
    return response_object


@router.get("/", response_model=List[NoteDB])
async def read_all_notes(session: Session = Depends(get_db)):
    return await notes.get_all(session)


@router.get("/{id}/", response_model=NoteSchema)
async def read_note(id: int, session: Session = Depends(get_db)):
    note = await notes.get(session, id)
    if not note:
        raise HTTPException(status_code=404, detail="Note not found")
    return note

# @router.put(
#     "/{note_id}",
#     tags=["custom"],
#     responses={403: {"description": "Operation forbidden"}},
# )
# async def update_note(note_id: str):
#     if note_id != "plumbus":
#         raise HTTPException(
#             status_code=403, detail="You can only update the item: plumbus"
#         )
#     return {"note_id": note_id, "name": "The great Plumbus"}


# @router.delete("/{note_id}",
#                response_model=Status,
#                responses={404: {"description": "Item not found"}})
# async def delete_note(note_id: str):
#     deleted_count = await Note.filter(id=note_id).delete()
#     if not deleted_count:
#         raise HTTPException(
#             status_code=404, detail=f"Note {note_id} not found")
#     return Status(message=f"Deleted note {note_id}")
