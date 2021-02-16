import datetime
from typing import List

from fastapi import APIRouter, Depends, Request, HTTPException
from fastapi.responses import RedirectResponse
from sqlalchemy.exc import SQLAlchemyError
from sqlalchemy.orm import Session
from starlette.status import HTTP_302_FOUND

from app.database.models import Event, UserMenstrualPeriodLength
from app.dependencies import get_db, templates
from app.routers.event import create_event
from app.internal.utils import create_model, get_current_user

from loguru import logger


router = APIRouter(
    prefix="/menstrual_predictor",
    tags=["menstrual_predictor"],
    dependencies=[Depends(get_db)]
)

MENSTRUAL_PERIOD_CATEGORY_ID = 111


@router.get("/")
def join(request: Request, db: Session = Depends(get_db)):
    current_user_id = get_current_user(db).id

    if not is_user_signed_up_to_menstrual_predictor(db, current_user_id):
        logger.info('getting menstrual predictor')
        return templates.TemplateResponse("join_menstrual_predictor.html", {
            "request": request,
        })
    else:
        return RedirectResponse(url='/', status_code=HTTP_302_FOUND)


@router.get("/add-period-start/{start_date}")
def add_period_start(request: Request, start_date: str,
                     db: Session = Depends(get_db)):
    try:
        period_start_date = datetime.datetime.strptime(start_date, '%Y-%m-%d')
    except ValueError as err:
        logger.exception(err)
        raise HTTPException(
            status_code=400,
            detail="The given date doesn't match a date format YYYY-MM-DD")
    else:
        current_user_id = get_current_user(db).id
        user_period_length = is_user_signed_up_to_menstrual_predictor(
            db, current_user_id)

        remove_existing_period_dates(db, current_user_id)
        if user_period_length:
            add_3_month_predictions(
                db, user_period_length, period_start_date, current_user_id)
    logger.info('adding menstrual start date')
    return RedirectResponse('/', status_code=303)


@router.post("/")
async def submit_join_form(
    request: Request,
    db: Session = Depends(get_db)
):

    data = await request.form()
    current_user = get_current_user(session=db)

    user_menstrual_period_length = {
        "user_id": current_user.id,
        "period_length": data['avg_period_length'],
    }
    last_period_date = datetime.datetime.strptime(
        data['last_period_date'], '%Y-%m-%d')
    try:
        new_signed_up_to_period = create_model(
            session=db,
            model_class=UserMenstrualPeriodLength,
            **user_menstrual_period_length)
    except SQLAlchemyError:
        logger.info(
            f'User {new_signed_up_to_period.user_id}'
            'already signed up to the service, hurray')
        db.rollback()
    url = '/'
    generate_predicted_period_dates(
        db, data['avg_period_length'], last_period_date, current_user.id)

    return RedirectResponse(url=url, status_code=HTTP_302_FOUND)


@router.get("/get-period-dates/")
def get_period_days(request: Request, db: Session = Depends(get_db)):
    period_days = get_all_period_days(db, 1)
    gaps_list = []
    for i in range(len(period_days) - 1):
        gap = get_date_diff(period_days[i].start, period_days[i + 1].start)
        gaps_list.append(gap.days)
    logger.critical(get_list_avg(gaps_list))


def get_avg_period_gap(db: Session, user_id):
    period_days = get_all_period_days(db, user_id)
    gaps_list = []

    for i in range(len(period_days) - 1):
        gap = get_date_diff(period_days[i].start, period_days[i + 1].start)
        gaps_list.append(gap.days)
    return get_list_avg(gaps_list)


def get_date_diff(date_1: datetime, date_2: datetime):
    return date_2 - date_1


def get_list_avg(received_list: List):
    return sum(received_list) // len(received_list)


def remove_existing_period_dates(db: Session, user_id: int):
    (db.query(Event).
     filter(Event.owner_id == user_id).
     filter(Event.category_id == MENSTRUAL_PERIOD_CATEGORY_ID).
     filter(Event.start > datetime.datetime.now()).
     delete())
    db.commit()
    logger.info('Removed all period predictions to create new ones')


def generate_predicted_period_dates(
        db: Session,
        period_length: str,
        period_start_date: datetime,
        user_id: int):
    delta = datetime.timedelta(int(period_length))
    period_end_date = period_start_date + delta
    create_event(db, 'period', period_start_date, period_end_date,
                 user_id, category_id=MENSTRUAL_PERIOD_CATEGORY_ID)
    get_all_period_days(db, user_id=user_id)


def add_3_month_predictions(db, period_length, period_start_date, user_id):
    avg_gap = get_avg_period_gap(db, user_id)
    avg_gap_delta = datetime.timedelta(avg_gap)
    for i in range(4):
        generate_predicted_period_dates(
            db, period_length, period_start_date, user_id)
        period_start_date += avg_gap_delta
        logger.error(period_start_date)
    logger.error(avg_gap_delta)


def get_all_period_days(session: Session, user_id: int) -> List[Event]:
    """Returns all period days filtered by user id."""

    try:
        period_days = sorted((session.query(Event).
                              filter(Event.owner_id == user_id).
                              filter(Event.category_id
                                     == MENSTRUAL_PERIOD_CATEGORY_ID).
                              all()), key=lambda d: d.start)

    except SQLAlchemyError as err:
        logger.debug(err)
        return []
    else:
        return period_days


def is_user_signed_up_to_menstrual_predictor(session: Session, user_id: int):
    user_menstrual_period_length = session.query(
        UserMenstrualPeriodLength).filter(user_id == user_id).first()
    if user_menstrual_period_length:
        return user_menstrual_period_length.period_length
    else:
        return False
