import io
import re

from datetime import datetime, timedelta
from fastapi import APIRouter, Depends, File, Request, UploadFile
from loguru import logger
from starlette.responses import RedirectResponse
from starlette.status import HTTP_302_FOUND
from sqlalchemy.exc import SQLAlchemyError
from PIL import Image

from app import config
from app.database.database import get_db
from app.database.models import User, Event, UserEvent
from app.dependencies import MEDIA_PATH, templates

PICTURE_EXTENSION = config.PICTURE_EXTENSION
PICTURE_SIZE = config.AVATAR_SIZE
REGEX_EXTRACT_HOLIDAYS = re.compile(
    r'SUMMARY:(?P<title>.*)(\n.*){1,8}DTSTAMP:(?P<date>\w{8})',
    re.MULTILINE)

router = APIRouter(
    prefix="/profile",
    tags=["profile"],
    responses={404: {"description": "Not found"}},
)


def get_placeholder_user():
    return User(
        username='new_user',
        email='my@email.po',
        password='1a2s3d4f5g6',
        full_name='My Name',
        telegram_id=''
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

    return templates.TemplateResponse("profile.html", {
        "request": request,
        "user": user,
        "events": upcoming_events,
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
        return (delta, 0, width - delta, height)
    delta = (height - width) // 2
    return (0, delta, width, width + delta)


@router.get("/import_holidays")
def import_holidays(request: Request):
    # Made up user details until there's a user login system
    current_username = "Chuck Norris"

    return templates.TemplateResponse("holidays.html", {
        "request": request,
        "username": current_username
    })


@router.post("/update_holidays")
async def update_holidays(
        file: UploadFile = File(...), session=Depends(get_db)):
    icsfile = await file.read()
    holidays = get_holidays_from_file(icsfile.decode(), session)
    try:
        save_holidays_to_db(holidays, session)
    except SQLAlchemyError as ex:
        logger.error(ex)
    finally:
        url = router.url_path_for("profile")
        return RedirectResponse(url=url, status_code=HTTP_302_FOUND)


def get_holidays_from_file(file, session):
    """
    this function using regex to extract holiday title
    and date from standrd ics file
    :param file:standard ics file
    :param session:current connection
    :return:list of holidays events
    """
    parsed_holidays = REGEX_EXTRACT_HOLIDAYS.finditer(file)
    holidays = []
    for holiday in parsed_holidays:
        valid_ascii_chars_range = 128
        title = holiday.groupdict()['title'].strip()
        title_to_save = ''.join([i if ord(i) < valid_ascii_chars_range
                                 else '' for i in title])
        date = holiday.groupdict()['date'].strip()
        holiday = Event(
            title=title_to_save,
            start=datetime.strptime(date, '%Y%m%d'),
            end=datetime.strptime(date, '%Y%m%d') + timedelta(days=1),
            content='holiday',
            owner_id=session.query(User).filter_by(id=1).first().id
        )
        holidays.append(holiday)
    return holidays


def save_holidays_to_db(holidays, session):
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
