from typing import List

from sqlalchemy.exc import SQLAlchemyError

from app.database.database import SessionLocal
from app.database.models import Event


def get_stripped_keywords(keywords: str) -> str:
    '''Gets a string of keywords to search for from the user form
       and returns a stripped ready-to-db-search keywords string'''

    keywords = " ".join(keywords.split())
    keywords = keywords.replace(" ", ":* & ") + ":*"
    return keywords


def get_results_by_keywords(
                            session: SessionLocal,
                            keywords: str,
                            owner_id: int
                           ) -> List[Event]:
    """Returns possible results for a search in the 'events' database table

    Args:
        keywords (str): search string
        owner_id (int): current user id

    Returns:
        list: a list of events from the database matching the inserted keywords

    Uses PostgreSQL's built in 'Full-text search' feature
    (doesn't work with SQLite)"""

    keywords = get_stripped_keywords(keywords)

    try:
        return session.query(Event).filter(
            Event.owner_id == owner_id,
            Event.events_tsv.match(keywords)).all()

    except (SQLAlchemyError, AttributeError):
        return []
