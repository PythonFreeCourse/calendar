from datetime import datetime
from typing import Optional, Dict, Union

from sqlalchemy.orm import Session
from sqlalchemy.sql.expression import func

from app.database.models import InternationalDays


def get_international_day(
        international_day: Dict[str, Union[str, int]]
) -> InternationalDays:
    """Returns an international day object from the dictionary data.

        Args:
            international_day: A dictionary international day
                related information.

        Returns:
            A new international day object.
    """
    return InternationalDays(
        day=international_day["day"],
        month=international_day["month"],
        international_day=international_day["international_day"],
    )


def get_international_day_per_day(
        session: Session, date: datetime
) -> Optional[InternationalDays]:
    day_num = date.day
    month = date.month
    international_day = (session.query(InternationalDays)
                         .filter(InternationalDays.day == day_num)
                         .filter(InternationalDays.month == month)
                         .order_by(func.random())
                         .first()
                         )
    return international_day
