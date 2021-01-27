from datetime import date
from typing import Optional

from app.database.models import InternationalDays

from sqlalchemy.orm import Session
from sqlalchemy.sql.expression import func

TOTAL_DAYS = 366


def international_day_per_day(session: Session, date) -> Optional[InternationalDays]:
    day_num = date.day
    month = date.month.strftime("%B")
    international_day = session.international_day(InternationalDays).filter(
        InternationalDays.day == day_num and InternationalDays.month == month).order_by(func.random()).first()
    return international_day