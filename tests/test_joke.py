from app.database.models import Joke
from app.internal import jokes
from app.internal import load_jokes


def get_jokes_amount(session):
    return session.query(Joke).count()


def test_joke(client):
    resp = client.get('/joke')
    assert resp.ok
    assert resp.json


def test_get_a_joke(session, joke):
    assert jokes.get_a_joke(session).text == joke.text


def test_load_daily_jokes(session):
    load_jokes.load_daily_jokes(session)
    assert get_jokes_amount(session) > 0


def test_jokes_not_load_twice_to_db(session):
    load_jokes.load_daily_jokes(session)
    first_load_amount = get_jokes_amount(session)
    load_jokes.load_daily_jokes(session)
    assert first_load_amount == get_jokes_amount(session)
