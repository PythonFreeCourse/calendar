from datetime import date
from typing import Dict, Optional

from app.database.models import Quote, UserQuotes
from sqlalchemy.orm import Session
from sqlalchemy.sql.expression import func

TOTAL_DAYS = 366


def create_quote_object(quotes_fields: Dict[str, Optional[str]]) -> Quote:
    """This function create a quote object from given fields dictionary.
    It is used for adding the data from the json into the db"""
    return Quote(
        text=quotes_fields['text'],
        author=quotes_fields['author'],
        is_favorite=False
    )


def quote_per_day(
        session: Session, date: date = date.today()
) -> Optional[Quote]:
    """This function provides a daily quote, relevant to the current
    day of the year. The quote is randomally selected from a set
    of quotes matching to the given day"""
    day_num = date.timetuple().tm_yday
    quote = session.query(Quote).filter(
        Quote.id % TOTAL_DAYS == day_num).order_by(func.random()).first()
    return quote


def get_quotes(session, user_id):
    """Retrieves the users' favorite quotes from the database."""
    quotes = []
    user_quotes = session.query(UserQuotes).filter_by(user_id=user_id).all()
    for user_quote in user_quotes:
        quote = session.query(Quote).filter_by(id=user_quote.quote_id).first()
        quote.is_favorite = True
        quotes.append(quote)
    return quotes


def get_quote_id(session, quote):
    """Retrieve quote id given the text of the quote."""
    return session.query(Quote).filter_by(text=quote).first().id


def save_quote(session, user_id, quote):
    """Saves a quote in the database."""
    quote_id = get_quote_id(session, quote)
    record = session.query(UserQuotes).filter(
        UserQuotes.user_id == user_id, UserQuotes.quote_id == quote_id).first()
    if not record:
        user_quote = UserQuotes(user_id=user_id, quote_id=quote_id)
        session.add(user_quote)
        session.commit()


def remove_quote(session, user_id, quote):
    """Removes a quote from the database."""
    quote_id = get_quote_id(session, quote)
    record = session.query(UserQuotes).filter(
        UserQuotes.user_id == user_id, UserQuotes.quote_id == quote_id).first()
    if record:
        session.delete(record)
        session.commit()
