import json
import os
from typing import Callable, Dict, List, Union

from loguru import logger
from sqlalchemy.orm import Session

from app.database.models import Base, Quote, Zodiac, HebrewView
from app.internal import daily_quotes, zodiac, hebrew_date_view


def get_data_from_json(path: str) -> List[Dict[str, Union[str, int, None]]]:
    """This function reads all of the data from a specific JSON file.
    The json file consists of list of dictionaries"""
    try:
        with open(path, 'r', encoding='utf-8-sig') as f:
            json_content_list = json.load(f)
    except (IOError, ValueError):
        file_name = os.path.basename(path)
        logger.exception(
            f"An error occurred during reading of json file: {file_name}")
        return []
    return json_content_list


def is_table_empty(session: Session, table: Base) -> bool:
    return session.query(table).count() == 0


def load_data(
        session: Session, path: str,
        table: Base, object_creator_function: Callable) -> None:
    """This function loads the specific data to the db,
    if it wasn't already loaded"""
    if not is_table_empty(session, table):
        return None
    json_objects_list = get_data_from_json(path)
    objects = [
        object_creator_function(json_object)
        for json_object in json_objects_list]
    session.add_all(objects)
    session.commit()


def load_to_db(session) -> None:
    """This function loads all the data for features
    based on pre-defind json data"""
    load_data(
        session, 'app/resources/zodiac.json',
        Zodiac, zodiac.create_zodiac_object)
    load_data(
        session, 'app/resources/quotes.json',
        Quote, daily_quotes.create_quote_object)
    """The quotes JSON file content is copied from the free API:
    'https://type.fit/api/quotes'. I saved the content so the API
     won't be called every time the app is initialized."""
    load_data(
        session, 'app/resources/hebrew_view.json',
        HebrewView, hebrew_date_view.create_hebrew_dates_object)
    """The parashot and hebrew_view JSON files content 
    is copied from the free API:
    'https://www.hebcal.com/hebcal?v=1&cfg=json&maj=on&min=on&
    mod=on&nx=on&year=now&month=x&ss=on&mf=on&c=on&geo=geoname
    &geonameid=293397&m=50&s=on&d=on&D=on'."""
