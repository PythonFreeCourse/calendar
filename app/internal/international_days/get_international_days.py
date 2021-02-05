from datetime import date
from typing import Optional

from app.database.models import InternationalDays

from sqlalchemy.orm import Session
from sqlalchemy.sql.expression import func


def international_day_per_day(session: Session, date) -> Optional[InternationalDays]:
    day_num = date.day
    month = date.strftime("%B")
    international_day = session.query(InternationalDays).filter(InternationalDays.day == str(day_num))\
        .filter(InternationalDays.month == month).order_by(func.random()).first()
    return international_day