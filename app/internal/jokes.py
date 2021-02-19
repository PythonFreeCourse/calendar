from typing import Dict, Optional

from sqlalchemy.orm import Session
from sqlalchemy.sql.expression import func

from app.database.models import Joke


def get_joke(joke_: Dict[str, Optional[str]]) -> Joke:
    """Returns a Joke object from the dictionary data.

    Args:
        joke_: A dictionary joke related information.

    Returns:
        A new Joke object.
    """
    return Joke(
        text=joke_['text'],
    )


def get_a_joke(session: Session):
    return session.query(Joke).order_by(func.random()).first()
