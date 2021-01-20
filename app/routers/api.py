import datetime
import secrets

from app.database.database import get_db
from app.database.models import Event, Token, User
from app.dependencies import templates
from fastapi import APIRouter, Body, Depends, Request, HTTPException
from fastapi.encoders import jsonable_encoder
from fastapi.responses import JSONResponse
from sqlalchemy import and_, or_
from typing import Optional


def check_api_key(key: str, session=Depends(get_db)):
    if session.query(Token).filter_by(id=key).first() is None:
        raise HTTPException(status_code=400, detail="Token invalid")


router = APIRouter(
    prefix='/api',
    tags=['api'],
    dependencies=[Depends(check_api_key)],
    responses={404: {"description": "Not found"}},
)

key_gen_router = APIRouter(
    prefix='/api',
    tags=['api_key_generator'],
    responses={404: {"description": "Not found"}},
)


@key_gen_router.get("/docs")
async def serve_api_docs(
        request: Request, session=Depends(get_db)):

    user = session.query(User).filter_by(id=1).first()

    api_routes = [{'name': '/new_event',}, {'name': '/{date}'}]
    api_key = session.query(Token).filter_by(owner_id=user.id).first()
    session.close()
    no_api_key = True
    if api_key is not None:
        no_api_key = False
        api_key = api_key.id
    return templates.TemplateResponse("api_docs.html", {
        "request": request,
        "user": user,
        "routes": api_routes,
        "no_api_key": no_api_key,
        "api_key": api_key or ''
        })


@key_gen_router.post('/generate_key')
async def generate_key(request: Request, session=Depends(get_db)):
    data = await request.json()
    if data.get('refresh', False):
        session.query(Token).filter_by(owner_id=data['user']).delete()
    token = secrets.token_urlsafe(32)
    while session.query(Token).filter_by(id=token).first() is not None:
        token = secrets.token_urlsafe(32)
    session.add(Token(id=token, owner_id=data['user']))
    session.commit()
    session.close()
    return JSONResponse(jsonable_encoder({'key': token}))


@key_gen_router.post('/delete_key')
async def delete_key(request: Request, session=Depends(get_db)):
    data = await request.json()
    session.query(Token).filter_by(owner_id=data['user']).delete()
    session.commit()
    session.close()
    return JSONResponse(jsonable_encoder({'success': True}))



@router.get('/get_events')
async def get_events(
    request: Request,
    key: str,
    date: Optional[datetime.date] = datetime.date.today(),
    session=Depends(get_db),
):
    user = session.query(User).filter(User.token.has(id=key)).first()
    events = session.query(Event).filter_by(owner_id=user.id)\
    .filter(Event.start  < datetime.datetime(date.year, date.month, date.day + 1, 0, 0, 0),
    Event.end > datetime.datetime(date.year, date.month, date.day - 1, 23, 59, 59))\
    .all()
    return JSONResponse(jsonable_encoder([{
        key: value for key, value in event.__dict__.items()
    } for event in events]))


@router.post('/create_event', status_code=201)
async def new_event(
    request: Request,
    key: str,
    title: str = Body(None),
    content: str = Body(None),
    start_date: datetime.date = Body(None),
    end_date: datetime.date = Body(None),
    session=Depends(get_db),
):
    user = session.query(User).filter(User.token.has(id=key)).first()
    event = Event(title=title, content=content, start=start_date, end=end_date, owner_id=user.id)
    d = {key: value for key, value in event.__dict__.items()}
    session.add(event)
    session.commit()
    d['id'] = event.id
    session.close()
    return JSONResponse(jsonable_encoder(d))