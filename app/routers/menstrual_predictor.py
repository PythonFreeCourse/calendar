import datetime
from typing import List, Union

from fastapi import APIRouter, Depends, Request
from fastapi.responses import RedirectResponse
from sqlalchemy.exc import SQLAlchemyError
from sqlalchemy.orm import Session
from starlette.status import HTTP_302_FOUND
from starlette.templating import Jinja2Templates

from app.database.models import Event, UserMenstrualPeriodLength
from app.dependencies import get_db, templates
from app.routers.share import accept
from app.routers.event import create_event
from app.routers.user import create_user
from app.internal.utils import create_model, get_current_user

from loguru import logger


# templates = Jinja2Templates(directory="app/templates")

router = APIRouter(
    prefix="/menstrual_predictor",
    tags=["menstrual_predictor"],
    dependencies=[Depends(get_db)]
)

MENSTRUAL_PERIOD_CATEGORY_ID = 111

@router.get("/")
def join(request: Request, db: Session = Depends(get_db)):
    logger.info('getting menstrual predictor')
    return templates.TemplateResponse("join_menstrual_predictor.html", {
        "request": request,
        # TODO:
        # "invitations": get_all_invitations(session=db),
    })


@router.post("/")
async def submit_join_form(
    request: Request,
    db: Session = Depends(get_db)
):
    # user = create_user(username='shimi', password='lalala', email='shimi@shimi.com', language_id=0, session=db, language='hebrew')
    # event = create_event(db, 'period day', datetime.datetime.now(), datetime.datetime.now(), 1, category_id=MENSTRUAL_PERIOD_CATEGORY_ID)
    # db.add(event)
    # db.commit()
    data = await request.form()
    # url = router.url_path_for("view_invitations")
    current_user = get_current_user(session=db)
    
    logger.error(f'current user, {current_user.id}')
    logger.error(data['avg_period_length'])

    user_menstrual_period_length = {
        "user_id": current_user.id,
        "period_length": data['avg_period_length'],
    }
    last_period_date = datetime.datetime.strptime(data['last_period_date'], '%Y-%m-%d')
    try:
        new_signed_up_to_period = create_model(session=db, model_class=UserMenstrualPeriodLength, **user_menstrual_period_length)
    except SQLAlchemyError as err:
        logger.warning('User already signed up to the service, hurray')
        db.rollback()
    url = '/'
    # if not is_date_before_today(last_period_date):
    #     return RedirectResponse(url=url, status_code=HTTP_302_FOUND)
    generate_predicted_period_dates(db, data['avg_period_length'], last_period_date, current_user.id)
    period_days = get_all_period_days(db, user_id=current_user.id)
    logger.error(period_days)
    # logger.warning(data)
    # remove_existing_period_dates(db, user_id=current_user.id)
    period_days = get_all_period_days(db, user_id=current_user.id)
    for day in period_days:
        logger.error(day.start)

    return RedirectResponse(url=url, status_code=HTTP_302_FOUND)


def remove_existing_period_dates(db, user_id):
    period_days = (db.query(Event).
        filter(Event.owner_id == user_id).
        filter(Event.category_id == MENSTRUAL_PERIOD_CATEGORY_ID).
        filter(Event.start > datetime.datetime.now()).
        delete())
    # db.delete(period_days)
    db.commit()


def generate_predicted_period_dates(db, period_length, last_period_time, user_id):
    for i in range(int(period_length)):
        delta = datetime.timedelta(i + 1)
        period_date = last_period_time + delta
        event = create_event(db, 'period day', period_date, period_date, user_id, category_id=MENSTRUAL_PERIOD_CATEGORY_ID)
        # db.add(event)
    # db.commit()


def get_all_period_days(session: Session, user_id: int) -> List[Event]:
    """Returns all period days filter by user id."""

    try:
        period_days = list(session.query(Event).
        filter(Event.owner_id == user_id).
        filter(Event.category_id == MENSTRUAL_PERIOD_CATEGORY_ID).
        all())

    except SQLAlchemyError as err:
        logger.debug(err)
        return []
    else:
        return period_days


def is_date_before_today(received_date: datetime):
    return received_date < datetime.datetime.now()
