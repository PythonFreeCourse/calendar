from datetime import datetime
from typing import Dict, Union

from sqlalchemy import and_, or_
from sqlalchemy.orm import Session

from app.database.models import Zodiac


def get_zodiac(data: Dict[str, Union[str, int]]) -> Zodiac:
    """Returns a Zodiac object from the dictionary data.

    Args:
        data: A dictionary zodiac related information.

    Returns:
        A new Zodiac object.

    """
    return Zodiac(
        name=data['name'],
        start_month=data['start_month'],
        start_day_in_month=data['start_day_in_month'],
        end_month=data['end_month'],
        end_day_in_month=data['end_day_in_month'],
    )


def get_zodiac_of_day(session: Session, date: datetime) -> Zodiac:
    """Returns the Zodiac object for the specific day.

    Args:
        session: The database connection.
        date: The requested date.

    Returns:
        A Zodiac object.

    """
    first_month_of_sign_filter = and_(
        Zodiac.start_month == date.month,
        Zodiac.start_day_in_month <= date.day)

    second_month_of_sign_filter = and_(
        Zodiac.end_month == date.month,
        Zodiac.end_day_in_month >= date.day)

    zodiac = (session.query(Zodiac)
              .filter(or_(first_month_of_sign_filter,
                          second_month_of_sign_filter))
              .first()
              )

    return zodiac


# TODO: Call this function from the month view
def get_zodiac_of_month(session: Session, date: datetime) -> Zodiac:
    """Returns the Zodiac object for the specific month.

    Args:
        session: The database connection.
        date: The requested date.

    Returns:
        A Zodiac object.

    """
    zodiac = (session
              .query(Zodiac)
              .filter(Zodiac.end_month == date.month)
              .first()
              )
    return zodiac
