import json
from typing import Dict, List, Optional

from sqlalchemy.orm import Session

from app.database.models import InternationalDays


def get_international_days_from_json() -> List[Dict[str, Optional[str]]]:
    try:
        with open('app/resources/international_days(2).json', 'r') as datadays:
            international_days_list = json.load(datadays)["calender"]
    except (IOError, ValueError):
        return []
    return international_days_list


def add_international_days_to_db(session: Session) -> None:
    all_international_days = get_international_days_from_json()
    international_days_objects = [
        InternationalDays(day=str(day['day']), month=day['month'],
                          international_day=day['international_day'])
        for day in all_international_days
    ]
    session.add_all(international_days_objects)
    session.commit()


def is_international_days_table_empty(session: Session) -> bool:
    return session.query(InternationalDays).count() == 0


def load_daily_international_days(session: Session) -> None:
    if is_international_days_table_empty(session):
        add_international_days_to_db(session)
