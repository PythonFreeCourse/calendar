from app.database.models import Quote
from app.internal.quotes import load_quotes


# Tests for loading the quotes in the db:
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
