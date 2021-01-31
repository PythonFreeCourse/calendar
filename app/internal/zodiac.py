from datetime import date
from typing import Dict, Union

from sqlalchemy.orm import Session
from sqlalchemy import and_, or_

from app.database.models import Zodiac


def create_zodiac_object(zodiac_fields: Dict[str, Union[str, int]]) -> Zodiac:
    """This function create a zodiac object from given fields dictionary.
    It is used for adding the data from the json into the db"""
    return Zodiac(
        name=zodiac_fields['name'],
        start_month=zodiac_fields['start_month'],
        start_day_in_month=zodiac_fields['start_day_in_month'],
        end_month=zodiac_fields['end_month'],
        end_day_in_month=zodiac_fields['end_day_in_month']
        )


def get_zodiac_of_day(session: Session, date: date) -> Zodiac:
    """This function return a zodiac object
    according to the current day."""
    first_month_of_sign_filter = and_(
        Zodiac.start_month == date.month,
        Zodiac.start_day_in_month <= date.day)
    second_month_of_sign_filter = and_(
        Zodiac.end_month == date.month,
        Zodiac.end_day_in_month >= date.day)
    zodiac_obj = session.query(Zodiac).filter(
        or_(first_month_of_sign_filter, second_month_of_sign_filter)).first()
    return zodiac_obj


# TODO: Call this function from the month view
def get_zodiac_of_month(session: Session, date: date) -> Zodiac:
    """This function return a zodiac object
    according to the current month."""
    zodiac_obj = session.query(Zodiac).filter(
        Zodiac.end_month == date.month).first()
    return zodiac_obj
