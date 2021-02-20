from datetime import date
from typing import Dict, Optional

from sqlalchemy.orm import Session
from sqlalchemy.sql.expression import func

from app.database.models import Quote

TOTAL_DAYS = 366


def create_quote_object(quotes_fields: Dict[str, Optional[str]]) -> Quote:
    """This function create a quote object from given fields dictionary.
    It is used for adding the data from the json into the db"""
    return Quote(
        text=quotes_fields['text'],
        author=quotes_fields['author']
    )


def quote_per_day(
        session: Session, date: date = date.today()
) -> Optional[Quote]:
    """This function provides a daily quote, relevant to the current
    day of the year. The quote is randomally selected from a set
    of quotes matching to the given day"""
    day_num = date.timetuple().tm_yday
    quote = session.query(Quote).filter(
        Quote.id % TOTAL_DAYS == day_num).order_by(func.random()).first()
    return quote
