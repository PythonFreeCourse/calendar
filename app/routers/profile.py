import io

from app import config
from app.database.database import get_db
from app.database.models import User
from app.dependencies import MEDIA_PATH, templates
from app.routers.user_exercise import create_user_exercise
from sqlalchemy.orm import Session
from app.internal.on_this_day_events import get_on_this_day_events
from fastapi import APIRouter, Depends, File, Request, UploadFile
from PIL import Image
from starlette.responses import RedirectResponse
from starlette.status import HTTP_302_FOUND

PICTURE_EXTENSION = config.PICTURE_EXTENSION
PICTURE_SIZE = config.AVATAR_SIZE

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
        is_active_exercise=False,
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


@router.get("/start_exercise")
async def start_exercise(session: Session = Depends(get_db)):
    user = session.query(User).filter_by(id=1).first()

    # Update database
    user.is_active_exercise = True
    session.commit()

    # create user exercise
    create_user_exercise(session, user)
    url = router.url_path_for("profile")
    return RedirectResponse(url=url, status_code=HTTP_302_FOUND)


@router.get("/stop_exercise")
async def stop_exercise(session=Depends(get_db)):
    """
    Stop exercise
    set is_active_exercise to False
    """
    user = session.query(User).filter_by(id=1).first()

    # Update database
    user.is_active_exercise = False
    session.commit()

    url = router.url_path_for("profile")
    return RedirectResponse(url=url, status_code=HTTP_302_FOUND)


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
        return delta, 0, width - delta, height
    delta = (height - width) // 2
    return 0, delta, width, width + delta
