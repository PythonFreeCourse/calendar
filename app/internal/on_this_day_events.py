import json
from datetime import date, datetime
from typing import Dict

import requests
from app.database.models import WikipediaEvents
from sqlalchemy import func
from sqlalchemy.exc import SQLAlchemyError
from sqlalchemy.orm import Session
from sqlalchemy.orm.exc import NoResultFound
from loguru import logger


def insert_on_this_day_data(session: Session) -> Dict:
    now = datetime.now()
    day, month = now.day, now.month

    res = requests.get(
        f'https://byabbe.se/on-this-day/{month}/{day}/events.json')
    text = json.loads(res.text)
    res_events = text.get('events')
    res_date = text.get('date')
    res_wiki = text.get('wikipedia')
    session.add(WikipediaEvents(events=res_events,
                                date_=res_date, wikipedia=res_wiki))
    session.commit()
    return text


def get_on_this_day_events(session: Session) -> Dict:
    try:
        data = (session.query(WikipediaEvents).
                filter(
                    func.date(WikipediaEvents.date_inserted) == date.today()).
                one())

    except NoResultFound:
        data = insert_on_this_day_data(session)
    except (SQLAlchemyError, AttributeError) as e:
        logger.error(f'on this day failedwith error: {e}')
        data = {'events': [], 'wikipedia': 'https://en.wikipedia.org/'}
    return data
