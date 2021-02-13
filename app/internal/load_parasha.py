import json
from datetime import datetime

from app.database.models import Parasha
from sqlalchemy.orm import Session
from typing import Dict, List, Optional


def get_parashot_from_json() -> List[Dict[str, Optional[str]]]:
    """Reading all parashot from the a JSON file that have been copied from:
    'https://www.hebcal.com/hebcal?v=1&cfg=json&maj=on&min=on&mod=on&nx=on&year=now&month=x&ss=on
    &mf=on&c=on&geo=geoname&geonameid=293397&m=50&s=on'
    Each year the Json file will need to be re-updated
    according to this API in this way:

    def relevent_details(p):
    parashot_dict = {'name': p['title'], 'hebrew': p['hebrew'],
     'link': p['link'], 'date': p['date']}
    return parashot_dict


    def get_all_parashot():
    r = requests.get('https://www.hebcal.com/hebcal?v=1&cfg=json&
    maj=on&min=on&mod=on&nx=on&year=now&month=x&ss=on&mf=on&c=on&
    geo=geoname&geonameid=293397&m=50&s=on')
    items = r.json()['items']
    all_para = list(filter(lambda i: 'Parashat' in i['title'], items))
    return [relevent_details(p) for p in all_para]
    """

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
            date=datetime.strptime(parasha['date'], '%Y-%m-%d').date()
        )
        for parasha in parashot
    ]
    session.add_all(parashot_objects)
    session.commit()


def load_parashot_if_table_empty(session: Session) -> None:
    """loading parashot from file to db """
    if session.query(Parasha).count() == 0:
        add_parashot_to_db(session)


def get_weekly_parasha(db_session: Session) -> Parasha:
    """This function return a parashot object"""
    return db_session.query(Parasha)
