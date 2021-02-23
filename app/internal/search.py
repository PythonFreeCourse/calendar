from typing import List

from sqlalchemy.exc import SQLAlchemyError
from sqlalchemy.orm.session import Session

from app.database.models import Event


def get_results_by_keywords(
        session: Session, keywords: str, owner_id: int
) -> List[Event]:
    """Returns a list of Events matching the search query.

     The results are limited to Events owned by the current user.
     Uses PostgreSQL's built in 'Full-text search' feature, and
     doesn't work with SQLite.

    Args:
        session: The database connection.
        keywords: The search keywords.
        owner_id: The current user ID.

    Returns:
        A list of Events matching the search query.
    """
    keywords = _get_stripped_keywords(keywords)

    try:
        return (session.query(Event)
                .filter(Event.owner_id == owner_id,
                        Event.events_tsv.match(keywords))
                .all())

    except (SQLAlchemyError, AttributeError):
        return []


def _get_stripped_keywords(keywords: str) -> str:
    """Returns a valid database search keywords string.

    Args:
        keywords: The search keywords.

    Returns:
        A valid database search keywords string.
    """
    keywords = " ".join(keywords.split())
    keywords = keywords.replace(" ", ":* & ") + ":*"
    return keywords
