from datetime import date

from app.database.models import Quote
from app.internal.quotes import load_quotes, daily_quotes

DATE = date(2021, 1, 1)
DATE2 = date(2021, 1, 2)


def insert_quotes(session):
    quote = Quote(
        id=1, text='You have to believe in yourself.', author='Sun Tzu')
    quote2 = Quote(id=2, text='Wisdom begins in wonder.', author='Socrates')
    session.add(quote)
    session.add(quote2)
    session.commit()


# Tests for loading the quotes in the db:
def test_is_quotes_table_empty_when_quotes_not_exist(session):
    assert load_quotes.is_quotes_table_empty(session)


def test_is_quotes_table_empty_when_quotes_exist(session):
    insert_quotes(session)
    assert not load_quotes.is_quotes_table_empty(session)


def test_load_daily_quotes(session):
    load_quotes.load_daily_quotes(session)
    assert session.query(Quote).count() > 0


def test_load_daily_quotes_with_json_valueerror(mocker, session):
    mock_json_load = mocker.patch('json.load')
    mock_json_load.side_effect = ValueError
    load_quotes.load_daily_quotes(session)
    assert session.query(Quote).count() == 0


def test_quotes_not_load_twice_to_db(session):
    load_quotes.load_daily_quotes(session)
    first_quotes_amount = session.query(Quote).count()
    load_quotes.load_daily_quotes(session)
    assert first_quotes_amount == session.query(Quote).count()


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
