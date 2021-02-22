import datetime

from loguru import logger

from typing import List

from sqlalchemy.exc import SQLAlchemyError
from sqlalchemy.orm import Session

from app.database.models import Event, UserMenstrualPeriodLength

from app.routers.event import create_event


MENSTRUAL_PERIOD_CATEGORY_ID = 111


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
    (
        db.query(Event)
        .filter(Event.owner_id == user_id)
        .filter(Event.category_id == MENSTRUAL_PERIOD_CATEGORY_ID)
        .filter(Event.start > datetime.datetime.now())
        .delete()
    )
    db.commit()
    logger.info("Removed all period predictions to create new ones")


def generate_predicted_period_dates(
    db: Session,
    period_length: str,
    period_start_date: datetime,
    user_id: int,
):
    delta = datetime.timedelta(int(period_length))
    period_end_date = period_start_date + delta
    period_event = create_event(
        db,
        "period",
        period_start_date,
        period_end_date,
        user_id,
        category_id=MENSTRUAL_PERIOD_CATEGORY_ID,
    )
    return period_event


def add_3_month_predictions(db, period_length, period_start_date, user_id):
    avg_gap = get_avg_period_gap(db, user_id)
    avg_gap_delta = datetime.timedelta(avg_gap)
    generated_3_months = []
    for _ in range(4):
        generated_period = generate_predicted_period_dates(
            db,
            period_length,
            period_start_date,
            user_id,
        )
        generated_3_months.append(generated_period)
        period_start_date += avg_gap_delta
    logger.info(f"Generated predictions: {generated_3_months}")
    return generated_3_months


def get_all_period_days(session: Session, user_id: int) -> List[Event]:
    """Returns all period days filtered by user id."""

    try:
        period_days = sorted(
            (
                session.query(Event)
                .filter(Event.owner_id == user_id)
                .filter(Event.category_id == MENSTRUAL_PERIOD_CATEGORY_ID)
                .all()
            ),
            key=lambda d: d.start,
        )

    except SQLAlchemyError as err:
        logger.exception(err)
        return []
    else:
        return period_days


def is_user_signed_up_to_menstrual_predictor(session: Session, user_id: int):
    user_menstrual_period_length = (
        session.query(UserMenstrualPeriodLength)
        .filter(user_id == user_id)
        .first()
    )
    if user_menstrual_period_length:
        return user_menstrual_period_length.period_length
    else:
        return False
