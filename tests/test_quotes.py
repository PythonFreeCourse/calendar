from datetime import date

from app.internal import daily_quotes
from app.internal.security.dependencies import current_user
from app.main import app
from app.routers.favorite_quotes import router
from tests.test_login import test_login_successfull

DATE = date(2021, 1, 1)
DATE2 = date(2021, 1, 2)
HOME_URL = app.url_path_for("home")
SAVE_URL = router.url_path_for("save_quote")
DELETE_URL = router.url_path_for("delete_quote")
FAVORITE_QUOTES_URL = router.url_path_for("favorite_quotes")


def test_get_quote():
    quotes_fields = {
        "text": "some_quote",
        "author": "Freud",
    }
    result = daily_quotes.get_quote(quotes_fields)
    assert result.text == "some_quote"
    assert result.author == "Freud"


def test_get_quote_of_day_no_quotes(session):
    assert daily_quotes.get_quote_of_day(session, DATE) is None


def test_get_quote_of_day_get_first_quote(session, quote1, quote2):
    assert daily_quotes.get_quote_of_day(session, DATE).text == quote1.text


def test_get_quote_of_day_get_second_quote(session, quote1, quote2):
    assert daily_quotes.get_quote_of_day(session, DATE2).text == quote2.text


def test_save_quote(session, quotes_test_client, quote1):
    test_login_successfull(session, quotes_test_client)
    data = {
        "quote_id": quote1.id,
        "author": quote1.author,
        "to_save": True,
        "user": current_user,
    }
    quotes = daily_quotes.get_quotes(session, 1)
    response = quotes_test_client.post(url=SAVE_URL, data=data)
    assert response.ok
    assert len(daily_quotes.get_quotes(session, 1)) == len(quotes) + 1


def test_delete_quote(session, quotes_test_client, quote1):
    test_save_quote(session, quotes_test_client, quote1)
    data = {
        "quote_id": quote1.id,
        "to_save": False,
    }
    response = quotes_test_client.delete(url=DELETE_URL, data=data)
    assert response.ok
    assert len(daily_quotes.get_quotes(session, 1)) == 0


def test_quote_of_day(session, quotes_test_client, quote1):
    assert not daily_quotes.is_quote_favorite(session, 1, quote1)
    test_save_quote(session, quotes_test_client, quote1)
    assert daily_quotes.is_quote_favorite(session, 1, quote1)


def test_get_favorite_quotes(session, quotes_test_client, quote1):
    test_save_quote(session, quotes_test_client, quote1)
    response = quotes_test_client.get(url=FAVORITE_QUOTES_URL)
    assert response.ok
    assert b"Favorite Quotes" in response.content


def test_home(session, quotes_test_client, quote1):
    response = quotes_test_client.get(url=HOME_URL)
    assert response.ok
    assert b"Search" in response.content
