from operator import attrgetter
from typing import List

from fastapi import APIRouter, Request

from app.database.models import Event
from app.database.models import UserEvent
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


def check_validation(start_time, end_time) -> bool:
    """Check if the start_date is smaller then the end_time"""

    try:
        return start_time < end_time
    except TypeError:
        return False



def add_new_event(values: dict, db) -> Event:
    """Get User values and the DB Session insert the values to the DB and refresh it
    exception in case that the keys in the dict is not match to the fields in the DB
    return the Event Class item"""

    try:
        if check_validation(values['start'], values['end']):
            new_event = create_model(
                        db, Event,
                        **values)
            return new_event
        else:
            return None
    except (AssertionError, AttributeError) as e:
        # Need to write into log
        print(e)
        return None


# start of endpoint ->
# @router.get("/profile/{user_id}/EditEvent", response_class=HTMLResponse)
# async def insert_info(request: Request) -> HTMLResponse:
#     """Get request and return an html File"""
#     return templates.TemplateResponse("editevent.html",{"request": request})


# @router.post("/profile/{user_id}/EditEvent") # this func is soupose to change with the PR of Ode and Efrat and it will be change
# def create_event(user_id: int, event_title: str = Form(None), location: Optional[str] = Form(None), from_date: Optional[datetime] = Form(...),
#                 to_date: Optional[datetime] = Form(...), link_vc: str = Form(None), content: str = Form(None),
#                  db = Depends(get_db)) -> dict:
#     """ required args - title, from_date, to_date, user_id, the 'from_date' need to be early from the 'to_date'.
#     check validation for the value, insert the new data to DB 
#     if the prosess success return True arg the event item, otherwith return False and the error msg """
#     success = False
#     error_msg = ""
#     new_event = ""
#     if event_title is None:
#         event_title = "No Title"
#     try:
#         if check_validation(from_date, to_date):
#             event_value = {'title': event_title, "location": location, "start_date": from_date, "end_date": to_date, "vc_link":link_vc, "content": content, 
#                 "owner_id": user_id}
#             new_event = add_event(event_value, db)
#             success = True
#         else:
#             error_msg = "Error, Your date is invalid"
#     except Exception as e:
#         error_msg = e
#     finally:
#         return {"success": success, "new_event": new_event, "error_msg": error_msg}
