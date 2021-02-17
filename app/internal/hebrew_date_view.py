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
        date=datetime.strptime(hebrew_dates_fields['date_gregorian'], '%Y-%m-%d').date(),
        hebrew_date=hebrew_dates_fields['date_hebrew']
    )


def get_all_hebrew_dates_list(db_session: Session) \
        -> List[Dict[str, Optional[str]]]:
    """This function return all hebrew dates object in list"""
    return db_session.query(HebrewView).all()
