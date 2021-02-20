from typing import Any, Dict, List

from fastapi import APIRouter, Request, status, HTTPException
from fastapi.param_functions import Depends
from sqlalchemy.orm import Session
from starlette.responses import RedirectResponse

from app.database.schemas import NoteDB, NoteSchema
from app.dependencies import get_db, templates
from app.internal.notes import notes


router = APIRouter(
    prefix="/notes",
    tags=["notes"],
    responses={404: {"description": "Not found"}},
)


@router.post(
    "/form_add", status_code=status.HTTP_201_CREATED, include_in_schema=False
)
async def create_note_by_form(
    request: Request, session: Session = Depends(get_db)
) -> RedirectResponse:
    form = await request.form()
    new_note = NoteSchema(**dict(form))
    await notes.create_note(note=new_note, session=session)
    return RedirectResponse("/notes", status_code=status.HTTP_302_FOUND)


@router.post("/", response_model=NoteDB, status_code=status.HTTP_201_CREATED)
async def create_new_note(
    request: NoteSchema, session: Session = Depends(get_db)
) -> Dict[str, Any]:
    new_note = NoteSchema(**dict(request))
    return await notes.create_note(note=new_note, session=session)


@router.delete("/{id}/", status_code=status.HTTP_200_OK)
async def delete_note(id: int, session: Session = Depends(get_db)):
    return await notes.delete(session, id)
    # return RedirectResponse("/notes", status_code=status.HTTP_302_FOUND)


@router.put(
    "/view/{id}", status_code=status.HTTP_202_ACCEPTED, include_in_schema=False
)
async def change_note(
    request: NoteSchema, id: int, session: Session = Depends(get_db)
):
    await notes.update(request, session, id)
    return RedirectResponse("/notes", status_code=status.HTTP_302_FOUND)


@router.put("/{id}/", status_code=status.HTTP_202_ACCEPTED)
async def update_note(
    request: NoteSchema, id: int, session: Session = Depends(get_db)
):
    return await notes.update(request, session, id)


@router.get("/view/{id}", include_in_schema=False)
async def view_note(
    request: Request, id: int, session: Session = Depends(get_db)
) -> templates:
    note = await notes.view(session, id)
    return templates.TemplateResponse(
        "notes/note_view.html", {"request": request, "data": note}
    )


@router.get("/add", include_in_schema=False)
async def create_note_form(request: Request) -> templates:
    return templates.TemplateResponse("notes/note.html", {"request": request})


@router.get("/all", response_model=List[NoteDB])
async def get_all_notes(session: Session = Depends(get_db)) -> List[NoteDB]:
    return await notes.get_all(session)


@router.get("/{id}/", status_code=status.HTTP_200_OK, response_model=NoteDB)
async def read_note(id: int, session: Session = Depends(get_db)) -> NoteDB:
    note = await notes.view(session, id)
    if not note:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Note with id {id} not found",
        )
    return note


@router.get("/", include_in_schema=False)
async def view_notes(
    request: Request, session: Session = Depends(get_db)
) -> templates:
    data = await notes.get_all(session)
    return templates.TemplateResponse(
        "notes/notes.html", {"request": request, "data": data}
    )
