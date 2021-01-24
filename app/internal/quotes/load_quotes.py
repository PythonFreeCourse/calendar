import json
from typing import Dict, List

from app.database.models import Quote

from sqlalchemy.orm import Session


def get_quotes_from_json() -> List[Dict]:
    """This function reads all of the daily quotes from a specific JSON file.
    The JSON file content is copied from the free API:
    'https://type.fit/api/quotes'. I saved the content so the API won't be
    called every time the app is initialized."""
    try:
        with open('app/resources/quotes.json', 'r') as f:
            quotes_list = json.load(f)
    except (IOError, ValueError):
        return []
    return quotes_list


def add_quotes_to_db(session: Session) -> None:
    """This function reads the quotes and inserts them into the db"""
    all_quotes = get_quotes_from_json()
    quotes_objects = [
        Quote(text=quote['text'], author=quote['author'])
        for quote in all_quotes
        ]
    session.add_all(quotes_objects)
    session.commit()


def is_quotes_table_empty(session: Session) -> bool:
    return session.query(Quote).count() == 0


def load_daily_quotes(session: Session) -> None:
    """This function loads the daily quotes to the db,
    if they weren't already loaden"""
    if is_quotes_table_empty(session):
        add_quotes_to_db(session)
