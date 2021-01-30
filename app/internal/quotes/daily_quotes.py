from datetime import date
from typing import Optional

from app.database.models import Quote

from sqlalchemy.orm import Session
from sqlalchemy.sql.expression import func

TOTAL_DAYS = 366


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
