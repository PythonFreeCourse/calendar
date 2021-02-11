from fastapi.param_functions import Depends
from sqlalchemy.orm import Session
from app.database.schemas import NoteDB, NoteSchema
from app.dependencies import get_db
from app.routers.notes import crud
from fastapi import APIRouter

router = APIRouter(
    prefix="/notes",
    tags=["notes"],
    responses={404: {"description": "Not found"}},
)


@router.post("/", response_model=NoteDB, status_code=201)
async def create_note(payload: NoteSchema, session: Session = Depends(get_db)):
    note_id = await crud.post(session, payload)

    response_object = {
        "id": note_id,
        "title": payload.title,
        "description": payload.description,
    }
    return response_object


# @router.get("/")
# async def get_all_notes():
#     return fake_notes_db


# @router.get("/{note_id}")
# async def get_note_by_id(note_id: str):
#     if note_id not in fake_notes_db:
#         raise HTTPException(status_code=404, detail="Item not found")
#     return {"name": fake_notes_db[note_id]["name"], "note_id": note_id}


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
