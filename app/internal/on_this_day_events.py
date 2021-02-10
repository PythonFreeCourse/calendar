from datetime import date, datetime
import json
from typing import Any, Dict

from fastapi import Depends
from loguru import logger
import requests
from sqlalchemy import func
from sqlalchemy.exc import SQLAlchemyError
from sqlalchemy.orm import Session
from sqlalchemy.orm.exc import NoResultFound

from app.database.models import WikipediaEvents
from app.dependencies import get_db


def insert_on_this_day_data(
        db: Session = Depends(get_db)
) -> Dict[str, Any]:
    now = datetime.now()
    day, month = now.day, now.month

    res = requests.get(
        f'https://byabbe.se/on-this-day/{month}/{day}/events.json')
    text = json.loads(res.text)
    res_events = text.get('events')
    res_date = text.get('date')
    res_wiki = text.get('wikipedia')
    db.add(WikipediaEvents(events=res_events,
                           date_=res_date, wikipedia=res_wiki))
    db.commit()
    return text


def get_on_this_day_events(
        db: Session = Depends(get_db)
) -> Dict[str, Any]:
    try:
        data = (db.query(WikipediaEvents).
                filter(
            func.date(WikipediaEvents.date_inserted) == date.today()).
                one())

    except NoResultFound:
        data = insert_on_this_day_data(db)
    except (SQLAlchemyError, AttributeError) as e:
        logger.error(f'on this day failed with error: {e}')
        data = {'events': [], 'wikipedia': 'https://en.wikipedia.org/'}
    return data
