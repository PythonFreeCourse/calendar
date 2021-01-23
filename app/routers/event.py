import re
from datetime import datetime as dt
from fastapi import APIRouter, Request, Depends, HTTPException
from fastapi.responses import RedirectResponse
from starlette.status import HTTP_303_SEE_OTHER

from app.database.database import get_db
from app.database.models import Event, User
from app.dependencies import templates

ZOOM_REGEX = re.compile('https://.*?\.zoom.us/[a-z]/.[^.,\b\t\n]+')

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
async def create_event(request: Request, session=Depends(get_db)):
    data = await request.form()
    print(data)
    title = data['title']
    content = data['description']
    start = dt.strptime(data['start_date'] + ' ' + data['start_time'], '%Y-%m-%d %H:%M')
    end = dt.strptime(data['end_date'] + ' ' + data['end_time'], '%Y-%m-%d %H:%M')
    user = session.query(User).filter_by(id=1).first()
    owner_id = user.id
    location_type = data['location_type']
    is_zoom = location_type == 'vc_url'
    location = data['location']

    if is_zoom and not ZOOM_REGEX.findall(location):
        raise HTTPException(status_code=400, detail="VC type with no valid zoom link")
    event = Event(title=title, content=content, start=start, end=end, owner_id=owner_id)
    session.add(event)
    session.commit()
    return RedirectResponse(f'/event/view/{event.id}', status_code=HTTP_303_SEE_OTHER)


@router.get("/view/{id}")
async def eventview(request: Request, id: int):
    return templates.TemplateResponse("event/eventview.html",
                                      {"request": request, "event_id": id})
