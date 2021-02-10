import io
import re

from datetime import datetime, timedelta
from loguru import logger
from fastapi import APIRouter, Depends, File, Request, UploadFile
from PIL import Image
from starlette.responses import RedirectResponse
from starlette.status import HTTP_302_FOUND
from sqlalchemy.exc import SQLAlchemyError
from sqlalchemy.orm import Session
from typing import List, Match

from app import config
from app.database.database import get_db
from app.database.models import User, Event, UserEvent
from app.dependencies import MEDIA_PATH, templates
from app.internal.on_this_day_events import get_on_this_day_events

PICTURE_EXTENSION = config.PICTURE_EXTENSION
PICTURE_SIZE = config.AVATAR_SIZE
REGEX_EXTRACT_HOLIDAYS = re.compile(
    r'SUMMARY:(?P<title>.*)(\n.*){1,8}DTSTAMP:(?P<date>\w{8})',
    re.MULTILINE)

router = APIRouter(
    prefix="/profile",
    tags=["profile"],
    responses={404: {"description": _("Not found")}},
)


def get_placeholder_user():
    return User(
        username='new_user',
        email='my@email.po',
        password='1a2s3d4f5g6',
        full_name='My Name',
        language_id=1,
        telegram_id='',
        language='english',
    )


@router.get("/")
async def profile(
        request: Request,
        session=Depends(get_db),
        new_user=Depends(get_placeholder_user)):
    # Get relevant data from database
    upcoming_events = range(5)
    user = session.query(User).filter_by(id=1).first()
    if not user:
        session.add(new_user)
        session.commit()
        user = session.query(User).filter_by(id=1).first()

    signs = ['Aries', 'Taurus', 'Gemini', 'Cancer', 'Leo',
             'Virgo', 'Libra', 'Scorpio', 'Sagittarius',
             'Capricorn', 'Aquarius', 'Pisces']
    on_this_day_data = get_on_this_day_events(session)

    return templates.TemplateResponse("profile.html", {
        "request": request,
        "user": user,
        "events": upcoming_events,
        "signs": signs,
        "on_this_day_data": on_this_day_data,
    })


@router.post("/update_user_fullname")
async def update_user_fullname(
        request: Request, session=Depends(get_db)):
    user = session.query(User).filter_by(id=1).first()
    data = await request.form()
    new_fullname = data['fullname']

    # Update database
    user.full_name = new_fullname
    session.commit()

    url = router.url_path_for("profile")
    return RedirectResponse(url=url, status_code=HTTP_302_FOUND)


@router.post("/update_user_email")
async def update_user_email(
        request: Request, session=Depends(get_db)):
    user = session.query(User).filter_by(id=1).first()
    data = await request.form()
    new_email = data['email']

    # Update database
    user.email = new_email
    session.commit()

    url = router.url_path_for("profile")
    return RedirectResponse(url=url, status_code=HTTP_302_FOUND)


@router.post("/update_user_description")
async def update_profile(
        request: Request, session=Depends(get_db)):
    user = session.query(User).filter_by(id=1).first()
    data = await request.form()
    new_description = data['description']

    # Update database
    user.description = new_description
    session.commit()

    url = router.url_path_for("profile")
    return RedirectResponse(url=url, status_code=HTTP_302_FOUND)


@router.post("/upload_user_photo")
async def upload_user_photo(
        file: UploadFile = File(...), session=Depends(get_db)):
    user = session.query(User).filter_by(id=1).first()
    pic = await file.read()

    try:
        # Save to database
        user.avatar = await process_image(pic, user)
        session.commit()

    finally:
        url = router.url_path_for("profile")
        return RedirectResponse(url=url, status_code=HTTP_302_FOUND)


@router.post("/update_telegram_id")
async def update_telegram_id(
        request: Request, session=Depends(get_db)):
    user = session.query(User).filter_by(id=1).first()
    data = await request.form()
    new_telegram_id = data['telegram_id']

    # Update database
    user.telegram_id = new_telegram_id
    session.commit()

    url = router.url_path_for("profile")
    return RedirectResponse(url=url, status_code=HTTP_302_FOUND)


@router.get("/holidays/import")
def import_holidays(request: Request):
    return templates.TemplateResponse("import_holidays.html", {
        "request": request,
    })


async def process_image(image, user):
    img = Image.open(io.BytesIO(image))
    width, height = img.size
    crop_area = get_image_crop_area(width, height)
    cropped = img.crop(crop_area)
    cropped.thumbnail(PICTURE_SIZE)
    file_name = f"{user.username}{PICTURE_EXTENSION}"
    cropped.save(f"{MEDIA_PATH}/{file_name}")
    return file_name


def get_image_crop_area(width, height):
    if width > height:
        delta = (width - height) // 2
        return delta, 0, width - delta, height
    delta = (height - width) // 2
    return 0, delta, width, width + delta


@router.post("/holidays/update")
async def update_holidays(
        file: UploadFile = File(...), session=Depends(get_db)):
    icsfile = await file.read()
    holidays = get_holidays_from_file(icsfile.decode(), session)
    try:
        save_holidays_to_db(holidays, session)
    except SQLAlchemyError as ex:
        logger.exception(ex)
    finally:
        url = router.url_path_for("profile")
        return RedirectResponse(url=url, status_code=HTTP_302_FOUND)


def get_holidays_from_file(file: List[Event], session: Session) -> List[Event]:
    """
    This function using regex to extract holiday title
    and date from standrd ics file
    :param file:standard ics file
    :param session:current connection
    :return:list of holidays events
    """
    parsed_holidays = REGEX_EXTRACT_HOLIDAYS.finditer(file)
    holidays = []
    for holiday in parsed_holidays:
        holiday_event = create_holiday_event(
            holiday, session.query(User).filter_by(id=1).first().id)
        holidays.append(holiday_event)
    return holidays


def create_holiday_event(holiday: Match[str], owner_id: int) -> Event:
    valid_ascii_chars_range = 128
    title = holiday.groupdict()['title'].strip()
    title_to_save = ''.join(i if ord(i) < valid_ascii_chars_range
                            else '' for i in title)
    date = holiday.groupdict()['date'].strip()
    format_string = '%Y%m%d'
    holiday = Event(
        title=title_to_save,
        start=datetime.strptime(date, format_string),
        end=datetime.strptime(date, format_string) + timedelta(days=1),
        content='holiday',
        owner_id=owner_id
    )
    return holiday


def save_holidays_to_db(holidays: List[Event], session: Session):
    """
    this function saves holiday list into database.
    :param holidays: list of holidays events
    :param session: current connection
    """
    session.add_all(holidays)
    session.commit()
    session.flush(holidays)
    userevents = []
    for holiday in holidays:
        userevent = UserEvent(
            user_id=holiday.owner_id,
            event_id=holiday.id
        )
        userevents.append(userevent)
    session.add_all(userevents)
    session.commit()
