from fastapi import APIRouter, Request

from app.database.models import Event, UserEvent
from app.dependencies import templates
from app.internal.utils import create_model

router = APIRouter(
    prefix="/event",
    tags=["event"],
    responses={404: {"description": "Not found"}},
)


@router.get("/edit")
async def eventedit(request: Request):
    return templates.TemplateResponse("event/eventedit.html",
                                      {"request": request})


@router.get("/view/{id}")
async def eventview(request: Request, id: int):
    return templates.TemplateResponse("event/eventview.html",
                                      {"request": request, "event_id": id})


def create_event(db, title, start, end, content, owner_id):

    event = create_model(
        db, Event,
        title=title,
        start=start,
        end=end,
        content=content,
        owner_id=owner_id,
    )
    create_model(
        db, UserEvent,
        user_id=owner_id,
        event_id=event.id
    )
    return event
