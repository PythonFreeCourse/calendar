from datetime import date
from os.path import relpath
from typing import Dict, List, Optional
from app.dependencies import MEDIA_PATH

from sqlalchemy.orm import Session
from sqlalchemy.sql.expression import func

from app.database.models import Quote, UserQuotes

EMPTY_HEART_PATH = relpath(f"{MEDIA_PATH}\\empty_heart.png", "app")
FULL_HEART_PATH = relpath(f"{MEDIA_PATH}\\full_heart.png", "app")
TOTAL_DAYS = 366


def get_quote(quote_: Dict[str, Optional[str]]) -> Quote:
    """Returns a Quote object from the dictionary data.

    Args:
        quote_: A dictionary quote related information.

    Returns:
        A new Quote object.
    """
    return Quote(
        text=quote_["text"],
        author=quote_["author"],
        is_favorite=False,
    )


def get_quote_of_day(
    session: Session,
    requested_date: date = date.today(),
) -> Optional[Quote]:
    """Returns the Quote object for the specific day.

    The quote is randomly selected from a set of quotes matching the given day.

    Args:
        session: The database connection.
        requested_date: Optional; The requested date.

    Returns:
        A Quote object.
    """
    day_number = requested_date.timetuple().tm_yday
    quote = (
        session.query(Quote)
        .filter(Quote.id % TOTAL_DAYS == day_number)
        .order_by(func.random())
        .first()
    )
    return quote


def get_quotes(session: Session, user_id: int) -> List[Quote]:
    """Retrieves the users' favorite quotes from the database."""
    quotes = []
    user_quotes = session.query(UserQuotes).filter_by(user_id=user_id).all()
    for user_quote in user_quotes:
        quote = session.query(Quote).filter_by(id=user_quote.quote_id).first()
        quotes.append(quote)
    return quotes


def is_quote_favorite(
    session: Session,
    user_id: int,
    quote_of_day: Quote,
) -> bool:
    """Checks if the daily quote is in favorites list."""
    if not quote_of_day:
        return False

    user_quotes = session.query(UserQuotes).filter_by(user_id=user_id).all()
    for user_quote in user_quotes:
        if user_quote.quote_id == quote_of_day.id:
            return True
    return False
