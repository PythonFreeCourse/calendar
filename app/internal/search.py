from app.database.database import SessionLocal
from app.database.models import Event
from sqlalchemy.exc import SQLAlchemyError


def get_results_by_keywords(session: SessionLocal, keywords: str, owner_id: int):
    """Returns possible results for a search in the 'events' database table.

    Args:
        keywords (str): search string
        owner_id (int): current user id

    Returns:
        list: a list of data from the database.

    Uses PostgreSQL's built in 'Full-text search' feature (doesn't work with SQLite)"""

    keywords = " ".join(keywords.split())
    keywords = keywords.replace(" ", ":* & ") + ":*"
    
    try: 
        return session.query(Event).filter(
        Event.owner_id == owner_id,
        Event.events_tsv.match(keywords)).all()

    except SQLAlchemyError:
        return []