import json
from datetime import datetime

from app.database.models import HebrewView
from sqlalchemy.orm import Session
from typing import Dict, List, Optional


def get_hebrew_view_from_json() -> List[Dict[str, Optional[str]]]:
    """Reading all hebrew dates from the a JSON file that have been copied from:
    'https://www.hebcal.com/hebcal?v=1&cfg=json&maj=on&min=on&mod=on&
    nx=on&year=now&month=x&ss=on&mf=on&c=on&
    geo=geoname&geonameid=293397&m=50&s=on&d=on&D=on'
    Each year the Json file will need to be re-updated
    according to this API in this way:

    def relevent_details(p):
    hebrew_dates_dict = {'date_gregorian': p['date'],
     'date_hebrew': p['hebrew']}
    return hebrew_dates_dict


    def get_all_hebrew_dates():
    r = requests.get('https://www.hebcal.com/hebcal?v=1&cfg=json&
    maj=on&min=on&mod=on&nx=on&year=now&month=x&ss=on&mf=on&c=on&
    geo=geoname&geonameid=293397&m=50&s=on&d=on&D=on')
    items = r.json()['items']

    all_hebrew_dates = list(filter(
    lambda i: 'hebdate' in i['category'], items))
    return [relevent_details(p) for p in all_hebrew_dates]
    """
    try:
        with open('app/resources/hebrew_view.json', encoding='utf-8-sig') as f:
            hebrew_dates_list = json.load(f)
    except (IOError, ValueError):
        return []
    return hebrew_dates_list


def add_hebrew_dates_to_db(session: Session) -> None:
    """This function reads the dates and inserts them into the db"""
    hebrew_dates = get_hebrew_view_from_json()
    hebrew_dates_objects = [
        HebrewView(
            date=datetime.strptime(hebrew_date['date_gregorian'],
                                   '%Y-%m-%d').date(),
            hebrew_date=hebrew_date['date_hebrew']
        )
        for hebrew_date in hebrew_dates
    ]
    session.add_all(hebrew_dates_objects)
    session.commit()


def load_hebrew_view_if_table_empty(session: Session) -> None:
    """loading hebrew dates from file to db """
    if session.query(HebrewView).count() == 0:
        add_hebrew_dates_to_db(session)


def get_hebrew_dates(db_session: Session) -> HebrewView:
    """This function return a list of hebrew dates
     of the current year object"""
    print(db_session.query(HebrewView))
    return print(db_session.query(HebrewView))
