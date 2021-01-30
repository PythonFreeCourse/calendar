from app.database.models import Quote
from app.internal.quotes import load_quotes


def get_quotes_amount(session):
    return session.query(Quote).count()


# Tests for loading the quotes in the db:
def test_load_daily_quotes(session):
    load_quotes.load_daily_quotes(session)
    assert get_quotes_amount(session) > 0


def test_load_daily_quotes_with_json_valueerror(mocker, session):
    mocker.patch('json.load', side_effect=ValueError)
    load_quotes.load_daily_quotes(session)
    assert get_quotes_amount(session) == 0


def test_quotes_not_load_twice_to_db(session):
    load_quotes.load_daily_quotes(session)
    first_quotes_amount = get_quotes_amount(session)
    load_quotes.load_daily_quotes(session)
    assert first_quotes_amount == get_quotes_amount(session)
