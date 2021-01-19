from fastapi import APIRouter, Request

from app.database.models import Event, UserEvent
from app.dependencies import templates
from app.internal.utils import save, create_model

router = APIRouter(
    prefix="/event",
    tags=["event"],
    responses={404: {"description": "Not found"}},
)


@router.get("/edit")
async def eventedit(request: Request):
    return templates.TemplateResponse("eventedit.html", {"request": request})


def create_event(db, title, start, end, content, owner_id):

    event = create_model(
        db, Event,
        title=title,
        start=start,
        end=end,
        content=content,
        owner_id=owner_id,
    )
    association = UserEvent(
        user_id=owner_id,
        event_id=event.id
    )
    save(association, session=db)
    return event
