from datetime import date

from app.database.models import Quote
from app.internal.quotes import daily_quotes

DATE = date(2021, 1, 1)
DATE2 = date(2021, 1, 2)


def insert_quotes(session):
    quote = Quote(
        id=1, text='You have to believe in yourself.', author='Sun Tzu')
    quote2 = Quote(id=2, text='Wisdom begins in wonder.', author='Socrates')
    session.add(quote)
    session.add(quote2)
    session.commit()


# Tests for providing a daily-quote from the db:
def test_quote_per_day_no_quotes(session):
    assert daily_quotes.quote_per_day(session, DATE) is None


def test_quote_per_day_get_first_quote(session):
    insert_quotes(session)
    assert daily_quotes.quote_per_day(
        session, DATE).text == 'You have to believe in yourself.'


def test_quote_per_day_get_second_quote(session):
    insert_quotes(session)
    assert daily_quotes.quote_per_day(
        session, DATE2).text == 'Wisdom begins in wonder.'
