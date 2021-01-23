from datetime import datetime as dt
from operator import attrgetter
from typing import List

from fastapi import APIRouter, Request
from fastapi import Depends
from fastapi.responses import RedirectResponse
from starlette.status import HTTP_303_SEE_OTHER

from app.database.database import get_db
from app.database.models import Event
from app.database.models import User
from app.database.models import UserEvent
from app.dependencies import templates
from app.internal.event import validate_zoom_link
from app.internal.utils import create_model
from app.routers.user import create_user

router = APIRouter(
    prefix="/event",
    tags=["event"],
    responses={404: {"description": "Not found"}},
)


@router.get("/edit")
async def eventedit(request: Request):
    return templates.TemplateResponse("event/eventedit.html",
                                      {"request": request})


@router.post("/edit")
async def create_new_event(request: Request, session=Depends(get_db)):
    data = await request.form()
    title = data['title']
    content = data['description']
    start = dt.strptime(data['start_date'] + ' ' + data['start_time'],
                        '%Y-%m-%d %H:%M')
    end = dt.strptime(data['end_date'] + ' ' + data['end_time'],
                      '%Y-%m-%d %H:%M')
    user = session.query(User).filter_by(id=1).first()
    user = user if user else create_user("u", "p", "e@mail.com", session)
    owner_id = user.id
    location_type = data['location_type']
    is_zoom = location_type == 'vc_url'
    location = data['location']

    if is_zoom:
        validate_zoom_link(location)

    event = create_event(session, title, start, end, owner_id, content,
                         location)
    return RedirectResponse(f'/event/view/{event.id}',
                            status_code=HTTP_303_SEE_OTHER)


@router.get("/view/{id}")
async def eventview(request: Request, id: int):
    return templates.TemplateResponse("event/eventview.html",
                                      {"request": request, "event_id": id})


def create_event(db, title, start, end, owner_id, content=None, location=None):
    """Creates an event and an association."""

    event = create_model(
        db, Event,
        title=title,
        start=start,
        end=end,
        content=content,
        owner_id=owner_id,
        location=location,
    )
    create_model(
        db, UserEvent,
        user_id=owner_id,
        event_id=event.id
    )
    return event


def sort_by_date(events: List[Event]) -> List[Event]:
    """Sorts the events by the start of the event."""

    temp = events.copy()
    return sorted(temp, key=attrgetter('start'))
