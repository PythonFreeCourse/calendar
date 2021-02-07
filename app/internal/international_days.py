from typing import Optional, Dict, Union

from sqlalchemy.orm import Session
from sqlalchemy.sql.expression import func

from app.database.models import InternationalDays


def create_international_day_object(
        international_day: Dict[str, Union[str, int]]) -> InternationalDays:
    return InternationalDays(
        day=international_day["day"],
        month=international_day["month"],
        international_day=international_day["international_day"]
    )


def get_international_day_per_day(session: Session, date) -> \
        Optional[InternationalDays]:
    day_num = int(date.day)
    month = int(date.strftime("%B"))
    international_day = session.query(InternationalDays).filter(
        InternationalDays.day == str(day_num)) \
        .filter(InternationalDays.month == month).order_by(
        func.random()).first()
    return international_day
