from datetime import date
from typing import Dict, Optional

from sqlalchemy.orm import Session
from sqlalchemy.sql.expression import func

from app.database.models import Quote

TOTAL_DAYS = 366


def get_quote(quote_: Dict[str, Optional[str]]) -> Quote:
    """Returns a Quote object from the dictionary data.

    Args:
        quote_: A dictionary quote related information.

    Returns:
        A new Quote object.
    """
    return Quote(
        text=quote_['text'],
        author=quote_['author'],
    )


def get_quote_of_day(
        session: Session, requested_date: date = date.today()
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
    quote = (session.query(Quote)
             .filter(Quote.id % TOTAL_DAYS == day_number)
             .order_by(func.random())
             .first()
             )
    return quote
