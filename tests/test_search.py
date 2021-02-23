from datetime import datetime

import pytest
from sqlalchemy.orm import Session

from app.config import PSQL_ENVIRONMENT
from app.database.models import Event, User
from app.internal.search import _get_stripped_keywords, get_results_by_keywords


class TestSearch:
    """Search feature tests.

    Works with PostgreSQL.

    """

    SEARCH = '/search'

    GOOD_KEYWORDS = [
        ({'keywords': 'lov'}, b'test'),
        ({'keywords': 'very    emotional'}, b'second event'),
        ({'keywords': 'event'}, b'My second event'),
        ({'keywords': 'event'}, b'My first event'),
        ({'keywords': 'jam'}, b'is fun'),
        ({'keywords': '    jam    '}, b'is fun'),
    ]

    BAD_KEYWORDS = [
        ({'keywords': ''}, b'Invalid'),
        ({'keywords': 'ev!@&'}, b'No matching'),
        ({'keywords': '[]'}, b'No matching'),
        ({'keywords': 'firsttttt'}, b'No matching'),
    ]

    NOT_PSQL_ENV_KEYWORDS = [
        ({'keywords': 'lov'}, b'No matching'),
        ({'keywords': 'very    emotional'}, b'No matching'),
        ({'keywords': 'event'}, b'No matching'),
        ({'keywords': 'jam'}, b'No matching'),
        ({'keywords': '    jam    '}, b'No matching'),
        ({'keywords': ''}, b'Invalid'),
    ]

    KEYWORDS_FOR_FUNC = [
        'lov',
        'very    emotional',
        'event',
        'jam',
        '    jam    ',
    ]

    STRIPPED_KEYWORDS = [
        ("      love string      ", "love:* & string:*"),
        ("test   ", "test:*"),
        ("i am awesome", "i:* & am:* & awesome:*"),
        ("a     lot    of       spaces", "a:* & lot:* & of:* & spaces:*"),
    ]

    @staticmethod
    def add_event(session: Session, title: str, content: str, owner_id: int):
        """Inserts an Event into the database.

        Args:
            session: The database fixture.
            title: The Event's title.
            content: The Event's content.
            owner_id: The User's ID.
        """
        event = Event(
            title=title,
            content=content,
            start=datetime.today(),
            end=datetime.today(),
            owner_id=owner_id,
        )

        session.add(event)
        session.commit()

    @staticmethod
    def create_event_data(session: Session, user: User):
        """Creates and adds Events to the database.

        Args:
            session: The database fixture.
            user: The User fixture.
        """
        events = [
            {
                'title': "My first event",
                'content': 'I am so excited',
            },
            {
                'title': "My second event",
                'content': 'I am very emotional',
            },
            {
                'title': "Pick up my nephews",
                'content': 'Very important',
            },
            {
                'title': "Solve this ticket",
                'content': 'I can do this',
            },
            {
                'title': "Jam with my friends",
                'content': "Jamming is fun",
            },
            {
                'title': 'test',
                'content': 'love string',
            }
        ]

        for event in events:
            TestSearch.add_event(session,
                                 title=event['title'],
                                 content=event['content'],
                                 owner_id=user.id,
                                 )

    @staticmethod
    def test_search_page_exists(client, session):
        response = client.get(TestSearch.SEARCH)
        assert response.ok
        assert b'Search event by keyword' in response.content


@pytest.mark.skipif(not PSQL_ENVIRONMENT, reason="Not PSQL environment")
@pytest.mark.parametrize('data, string', TestSearch.GOOD_KEYWORDS)
def test_search_good_keywords(data, string, client, session, user):
    TestSearch.create_event_data(session, user)
    resp = client.post(TestSearch.SEARCH, data=data)
    assert string in resp.content


@pytest.mark.skipif(not PSQL_ENVIRONMENT, reason="Not PSQL environment")
@pytest.mark.parametrize('data, string', TestSearch.BAD_KEYWORDS)
def test_search_bad_keywords(data, string, client, session, user):
    TestSearch.create_event_data(session, user)
    resp = client.post(TestSearch.SEARCH, data=data)
    assert string in resp.content


@pytest.mark.skipif(PSQL_ENVIRONMENT, reason="PSQL environment")
@pytest.mark.parametrize('data, string', TestSearch.NOT_PSQL_ENV_KEYWORDS)
def test_search_not_psql_env_keywords(data, string, client, session, user):
    TestSearch.create_event_data(session, user)
    response = client.post(TestSearch.SEARCH, data=data)
    assert string in response.content


@pytest.mark.skipif(PSQL_ENVIRONMENT, reason="Not PSQL environment")
@pytest.mark.parametrize('input_string', TestSearch.KEYWORDS_FOR_FUNC)
def test_get_results_by_keywords_func(input_string, client, session, user):
    TestSearch.create_event_data(session, user)
    assert not get_results_by_keywords(session, input_string, 1)


@pytest.mark.parametrize('input_string, output_string',
                         TestSearch.STRIPPED_KEYWORDS)
def test_search_stripped_keywords(input_string, output_string):
    assert _get_stripped_keywords(input_string) == output_string


def test_events_tsv_column_exists():
    column_created = True

    try:
        Event.events_tsv
    except AttributeError:
        column_created = False

    if PSQL_ENVIRONMENT:
        assert column_created
    else:
        assert not column_created
