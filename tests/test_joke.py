from app.database.models import Joke
from app.internal import jokes


def get_jokes_amount(session):
    return session.query(Joke).count()


def test_get_a_joke(session, joke):
    assert jokes.get_a_joke(session).text == joke.text


def test_jokes_not_load_twice_to_db(session):
    jokes.get_a_joke(session)
    first_load_amount = get_jokes_amount(session)
    jokes.get_a_joke(session)
    assert first_load_amount == get_jokes_amount(session)
