from app.database import models, schemas
from app.database.schemas import NoteDB, NoteSchema
from app.dependencies import get_db, templates
from app.internal.notes import notes
from fastapi import APIRouter, HTTPException, Request
from fastapi.param_functions import Depends
from sqlalchemy.orm import Session
from starlette.responses import RedirectResponse
from starlette.status import HTTP_302_FOUND
from typing import List


router = APIRouter(
    prefix="/notes",
    tags=["notes"],
    responses={404: {"description": "Not found"}},
)


@router.post("/add", response_model=NoteDB, status_code=201)
async def create_new_note(request: Request,
                          session: Session = Depends(get_db)) -> templates:
    form = await request.form()
    new_note = schemas.NoteSchema(**dict(form))
    await create_note(note=new_note, session=session)
    return RedirectResponse('/notes', status_code=HTTP_302_FOUND)


async def create_note(note: NoteSchema, session: Session) -> models.Note:
    note_id = await notes.post(session, note)
    response_object = {
        "id": note_id,
        "title": note.title,
        "description": note.description,
        "timestamp": note.timestamp,
    }
    return response_object


@router.get("/add")
async def create_note_form(request: Request) -> templates:
    return templates.TemplateResponse("notes/note.html",
                                      {"request": request})


@router.get("/", response_model=List[NoteDB])
async def get_all_notes(request: Request,
                        session: Session = Depends(get_db)) -> templates:
    data = await read_all_notes(session)
    return templates.TemplateResponse(
        "notes/notes.html",
        {'request': request, 'data': data})


async def read_all_notes(session: Session) -> List[NoteDB]:
    return await notes.get_all(session)


@router.get("/{id}/", response_model=NoteSchema)
async def read_note(id: int, session: Session = Depends(get_db)):
    note = await notes.get(session, id)
    if not note:
        raise HTTPException(status_code=404, detail="Note not found")
    return note


@router.put("/{id}/", response_model=NoteDB)
async def update_note(request: Request,
                      id: int,
                      payload: NoteSchema,
                      session: Session = Depends(get_db)):
    note = await notes.get(session, id)
    if not note:
        raise HTTPException(status_code=404, detail="Note not found")
    note_id = await notes.put(session, id, payload)
    response_object = {
        "id": note_id,
        "title": payload.title,
        "description": payload.description,
        "timestamp": payload.timestamp,
    }
    return response_object
    # return templates.TemplateResponse(
    #     "notes/note.html", {'request': request, 'data': response_object})


@router.delete("/{id}/", response_model=NoteDB)
async def delete_note(id: int, session: Session = Depends(get_db)):
    note = await notes.get(session, id)
    if not note:
        raise HTTPException(status_code=404, detail="Note not found")
    await notes.delete(session, id)
    return note
    # return RedirectResponse('/notes', status_code=HTTP_302_FOUND)
