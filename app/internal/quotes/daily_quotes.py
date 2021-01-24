from datetime import date
import random
from typing import Optional

from app.database.models import Quote

from sqlalchemy.orm import Session


def quote_per_day(
        session: Session, date: date = date.today()
        ) -> Optional[Quote]:
    """This function provides a daily quote, relevant to the current
    day of the year. The quote is randomally selected from a set
    of quotes matching to the given day"""
    day_num = date.timetuple().tm_yday
    quotes = session.query(Quote).filter(Quote.id % 366 == day_num).all()
    if len(quotes) > 0:
        return random.choice(quotes)
    return None
