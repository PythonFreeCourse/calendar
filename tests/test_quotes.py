from datetime import date

from app.internal import daily_quotes

DATE = date(2021, 1, 1)
DATE2 = date(2021, 1, 2)


def test_get_quote():
    quotes_fields = {
        'text': 'some_quote',
        'author': 'Freud',
    }
    result = daily_quotes.get_quote(quotes_fields)
    assert result.text == 'some_quote'
    assert result.author == 'Freud'


def test_get_quote_of_day_no_quotes(session):
    assert daily_quotes.get_quote_of_day(session, DATE) is None


def test_get_quote_of_day_get_first_quote(session, quote1, quote2):
    assert daily_quotes.get_quote_of_day(
        session, DATE).text == quote1.text


def test_get_quote_of_day_get_second_quote(session, quote1, quote2):
    assert daily_quotes.get_quote_of_day(
        session, DATE2).text == quote2.text
