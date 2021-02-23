from datetime import datetime
from typing import Dict, Optional
from pyluach import dates, parshios

from app.database.models import Parasha
from sqlalchemy.orm import Session


def create_parasha_object(parashot_fields: Dict[str, str]) -> Parasha:
    """This function create a parasha object from given fields dictionary.
    It is used for adding the data from the json into the db"""
    return Parasha(
        name=parashot_fields['name'],
        hebrew_name=parashot_fields['hebrew'],
        link=parashot_fields['link'],
    )


def get_parasha_only_to_saturday(date: datetime) -> Optional[str]:
    """Returns the parasha name if the date is Saturday.

     Args:
         date: The requested date.

     Returns:
         If the date is Saturday, return the parasha name,
         else return None.
    """
    date_split = str(date).split('-')
    new_date_format = [int(x) for x in date_split]
    gregorian_date = dates.GregorianDate(*new_date_format)
    if gregorian_date == gregorian_date.shabbos():
        return parshios.getparsha_string(gregorian_date)


def get_parasha_object(session: Session, date: datetime) -> Parasha:
    """Returns the parasha object for the specific day.

    Args:
        session: The database connection.
        date: The requested date.

    Returns:
        A HebrewView object.
        IF the specific day in not Saturday, it return None.
    """
    parasha_name = get_parasha_only_to_saturday(date)
    if parasha_name is None:
        return None
    for parasha in session.query(Parasha).all():
        if parasha_name in parasha.name:
            return parasha
