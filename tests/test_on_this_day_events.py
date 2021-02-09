from app.database.models import WikipediaEvents
from app.internal.on_this_day_events import (get_on_this_day_events,
                                             insert_on_this_day_data)


def test_insert_on_this_day_data(session):
    is_exists_data = session.query(WikipediaEvents).all()
    assert not is_exists_data
    insert_on_this_day_data(session)
    is_exists_data = session.query(WikipediaEvents).all()
    assert is_exists_data is not None


def test_get_on_this_day_events(session):
    data = get_on_this_day_events(session)
    assert isinstance(data, dict)
    assert isinstance(data.get('events'), list)
    assert isinstance(data.get('wikipedia'), str)


def test_get_on_this_day_events_exists(session):
    fake_object = WikipediaEvents(
        events=['fake'], wikipedia="www.fake.com", date_="not a date string")
    session.add(fake_object)
    session.commit()
    fake_data = get_on_this_day_events(session)
    assert fake_data.events[0] == 'fake'
    assert fake_data.wikipedia == 'www.fake.com'
    assert fake_data.date_ == 'not a date string'
