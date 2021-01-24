from datetime import datetime

import pytest
from app.config import PSQL_ENVIRONMENT
from app.database.models import Event, User
from app.internal.search import get_results_by_keywords, get_stripped_keywords
from fastapi import status


class TestSearch:
    '''Search feature test. Works with PostgreSQL'''

    SEARCH = '/search'
    GOOD_KEYWORDS = [
        ({'keywords': 'lov'}, b'test'),
        ({'keywords': 'very    emotional'}, b'second event'),
        ({'keywords': 'event'}, b'My second event'),
        ({'keywords': 'event'}, b'My first event'),
        ({'keywords': 'jam'}, b'is fun'),
        ({'keywords': '    jam    '}, b'is fun')
    ]
    BAD_KEYWORDS = [
        ({'keywords': ''}, b'Invalid'),
        ({'keywords': 'ev!@&'}, b'No matching'),
        ({'keywords': '[]'}, b'No matching'),
        ({'keywords': 'firsttttt'}, b'No matching')
    ]
    NOT_PSQL_ENV_KEYWORDS = [
        ({'keywords': 'lov'}, b'No matching'),
        ({'keywords': 'very    emotional'}, b'No matching'),
        ({'keywords': 'event'}, b'No matching'),
        ({'keywords': 'jam'}, b'No matching'),
        ({'keywords': '    jam    '}, b'No matching'),
        ({'keywords': ''}, b'Invalid')
    ]
    KEYWORDS_FOR_FUNC = [
        'lov',
        'very    emotional',
        'event',
        'jam',
        '    jam    '
    ]

    @staticmethod
    def create_user(session):
        user = User(username='testuser', email='test@abc.com', password='1234')
        session.add(user)
        session.commit()
        return user

    @staticmethod
    def add_event(session, title, content, owner_id):
        event = Event(
            title=title,
            content=content,
            start=datetime.today(),
            end=datetime.today(),
            owner_id=owner_id
        )

        session.add(event)
        session.commit()

    @staticmethod
    def create_data(session):
        TestSearch.create_user(session)
        events = [
                    {
                        'title': "My first event",
                        'content': 'I am so excited',
                        'owner_id': 1
                    },
                    {
                        'title': "My second event",
                        'content': 'I am very emotional',
                        'owner_id': 1
                    },
                    {
                        'title': "Pick up my nephews",
                        'content': 'Very important',
                        'owner_id': 1
                    },
                    {
                        'title': "Solve this ticket",
                        'content': 'I can do this',
                        'owner_id': 1
                    },
                    {
                        'title': "Jam with my friends",
                        'content': "Jamming is fun",
                        'owner_id': 1
                    },
                    {
                        'title': 'test',
                        'content': 'love string',
                        'owner_id': 1
                    }
                 ]

        for event in events:
            TestSearch.add_event(
                                    session,
                                    title=event['title'],
                                    content=event['content'],
                                    owner_id=event['owner_id']
                                )

    @staticmethod
    def test_search_page_exists(client):
        resp = client.get(TestSearch.SEARCH)
        assert resp.status_code == status.HTTP_200_OK
        assert b'Search event by keyword' in resp.content


@pytest.mark.skipif(not PSQL_ENVIRONMENT, reason="Not PSQL environment")
@pytest.mark.parametrize('data, string', TestSearch.GOOD_KEYWORDS)
def test_search_good_keywords(data, string, client, session):
    ts = TestSearch()
    ts.create_data(session)
    resp = client.post(ts.SEARCH, data=data)
    assert string in resp.content


@pytest.mark.skipif(not PSQL_ENVIRONMENT, reason="Not PSQL environment")
@pytest.mark.parametrize('data, string', TestSearch.BAD_KEYWORDS)
def test_search_bad_keywords(data, string, client, session):
    ts = TestSearch()
    ts.create_data(session)
    resp = client.post(ts.SEARCH, data=data)
    assert string in resp.content


@pytest.mark.skipif(PSQL_ENVIRONMENT, reason="PSQL environment")
@pytest.mark.parametrize('data, string', TestSearch.NOT_PSQL_ENV_KEYWORDS)
def test_search_not_psql_env_keywords(data, string, client, session):
    ts = TestSearch()
    ts.create_data(session)
    resp = client.post(ts.SEARCH, data=data)
    assert string in resp.content


@pytest.mark.skipif(PSQL_ENVIRONMENT, reason="Not PSQL environment")
@pytest.mark.parametrize('input_string', TestSearch.KEYWORDS_FOR_FUNC)
def test_get_results_by_keywords_func(input_string, client, session):
    ts = TestSearch()
    ts.create_data(session)
    assert not get_results_by_keywords(session, input_string, 1)


STRIPPED_KEYWORDS = [
    ("      love string      ", "love:* & string:*"),
    ("test   ", "test:*"),
    ("i am awesome", "i:* & am:* & awesome:*"),
    ("a     lot    of       spaces", "a:* & lot:* & of:* & spaces:*")
]


@pytest.mark.parametrize('input_string, output_string', STRIPPED_KEYWORDS)
def test_search_stripped_keywords(input_string, output_string):
    assert get_stripped_keywords(input_string) == output_string


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

        
