import re
from datetime import datetime as dt
from fastapi import APIRouter, Request, Depends, HTTPException
from fastapi.responses import RedirectResponse
from starlette.status import HTTP_303_SEE_OTHER

from app.database.database import get_db
from app.database.models import Event, User
from app.dependencies import templates

ZOOM_REGEX = re.compile(r'https://.*?\.zoom.us/[a-z]/.[^.,\b\t\n]+')
VALID_MAIL_REGEX = re.compile(r'^\S+@\S+\.\S+$')

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
    title = data['title']
    content = data['description']
    start = dt.strptime(data['start_date'] + ' ' + data['start_time'],
                        '%Y-%m-%d %H:%M')
    end = dt.strptime(data['end_date'] + ' ' + data['end_time'],
                      '%Y-%m-%d %H:%M')
    user = session.query(User).filter_by(id=1).first()
    if not user:
        user = User(
            username='new_user',
            email='my@email.po',
            password='1a2s3d4f5g6',
        )
    owner_id = user.id
    location_type = data['location_type']
    is_zoom = location_type == 'vc_url'
    location = data['location']

    if is_zoom and not ZOOM_REGEX.findall(location):
        raise HTTPException(status_code=400,
                            detail="VC type with no valid zoom link")

    invitees = []
    for invited_mail in data['invited'].split(','):
        invited_mail = invited_mail.strip()
        if VALID_MAIL_REGEX.fullmatch(invited_mail):
            invitees.append(invited_mail)

    event = Event(title=title, content=content, start=start, end=end,
                  owner_id=owner_id, invitees=','.join(invitees))

    regular_invitees = set()
    for record in session.query(Event).with_entities(Event.invitees).filter(Event.owner_id == owner_id,
                                                                            Event.title == title).all():
        for email in record[0].split(','):
            regular_invitees.add(email)

    uninvited_contacts = regular_invitees.difference(set(invitees))

    session.add(event)
    session.commit()

    message = f'Forgot to invite {", ".join(uninvited_contacts)} maybe?'
    return RedirectResponse(f'/event/view/{event.id}?message={message}',
                            status_code=HTTP_303_SEE_OTHER)


@router.get("/view/{id}")
async def eventview(request: Request, id: int):
    message = request.query_params.get('message', '')
    return templates.TemplateResponse("event/eventview.html",
                                      {"request": request, "event_id": id, "message": message})
