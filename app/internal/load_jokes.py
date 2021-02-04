import json
from typing import Dict, List, Optional

from app.database.models import Joke

from sqlalchemy.orm import Session


def get_jokes_from_json() -> List[Dict[str, Optional[str]]]:
    """Reading all jokes from the a JSON file that have been copied from 'http://api.icndb.com/jokes'"""
    try:
        with open('app/resources/jokes.json', 'r') as f:
            jokes_list = json.load(f)
    except (IOError, ValueError):
        return []
    return jokes_list


def add_jokes_to_db(session: Session) -> None:
    """This function reads the jokes and inserts them into the db"""
    all_jokes = get_jokes_from_json()
    jokes_objects = [
        Joke(text=joke['text'])
        for joke in all_jokes
        ]
    session.add_all(jokes_objects)
    session.commit()


def is_jokes_table_empty(session: Session) -> bool:
    return session.query(Joke).count() == 0


def load_daily_jokes(session: Session) -> None:
    """loading jokes from file to db """
    if is_jokes_table_empty(session):
        add_jokes_to_db(session)
