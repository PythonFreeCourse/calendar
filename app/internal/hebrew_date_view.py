from datetime import datetime
from typing import Dict, Optional, List

from app.database.models import HebrewView
from sqlalchemy.orm import Session


def create_hebrew_dates_object(
        hebrew_dates_fields: Dict[str, Optional[str]])\
        -> HebrewView:
    """This function create a hebrew date object
    from given fields dictionary.
    It is used for adding the data from the json into the db"""
    return HebrewView(
        date=datetime.strptime(
            hebrew_dates_fields['date_gregorian'],
            '%Y-%m-%d').date(),
        hebrew_date=hebrew_dates_fields['date_hebrew']
    )


def get_hebrew_date_object(session: Session, date: datetime) -> HebrewView:
    """Returns the HebrewView object for the specific day.

    Args:
        session: The database connection.
        date: The requested date.

    Returns:
        A HebrewView object.
    """
    for hebrew in session.query(HebrewView).all():
        if hebrew.date == date:
            return hebrew
