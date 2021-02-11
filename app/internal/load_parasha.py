import json
from datetime import datetime, date

from app.database.models import Parasha
from sqlalchemy.orm import Session
from typing import Dict, List, Optional


def get_parashot_from_json() -> List[Dict[str, Optional[str]]]:
    """Reading all parashot from the a JSON file that have been.copied from:
    'https://www.hebcal.com/hebcal?v=1&cfg=json&maj=on&min=on&mod=on&nx=on&year=now&month=x&ss=on&mf=on&c=on'
    '&geo=geoname&geonameid=293397&m=50&s=on'"""
    try:
        with open('app/resources/parashot.json', encoding='utf-8-sig') as f:
            parashot_list = json.load(f)
    except (IOError, ValueError):
        return []
    return parashot_list


def add_parashot_to_db(session: Session) -> None:
    """This function reads the parashot and inserts them into the db"""
    parashot = get_parashot_from_json()
    parashot_objects = [
    Parasha(
        name=parasha['name'],
        hebrew_name=parasha['hebrew'],
        link=parasha['link'],
        date=datetime.strptime(parasha['date'], '%Y-%m-%d').date())
    for parasha in parashot
    ]
    session.add_all(parashot_objects)
    session.commit()


def is_parashot_table_empty(session: Session) -> bool:
    return session.query(Parasha).count() == 0


def load_parashot(session: Session) -> None:
    """loading parashot from file to db """
    if is_parashot_table_empty(session):
        add_parashot_to_db(session)


def get_weekly_parasha(db_session: Session, date: date) -> Parasha:
    """This function return a parashot object"""
    date = None
    return db_session.query(Parasha)
