from app.database.models import Event, UserEvent
from app.internal.restore_events import delete_events_after_optionals_num_days

EVENT_TITLE = b'event'


def test_successful_deletion(event_test_client, session, event):
    event_test_client.delete("/event/1")
    response = event_test_client.get('/profile/restore_events')
    assert response.ok
    assert EVENT_TITLE in response.content


def test_successful_restore(event_test_client, session, event):
    event_test_client.delete("/event/1")
    response = event_test_client.post('/profile/restore_events',
                                      dict(check='on', id=1))
    assert response.ok
    assert EVENT_TITLE not in response.content


def test_successful_permanently_deletion(event_test_client, session, event):
    event_test_client.delete("/event/1")
    days = -1
    delete_events_after_optionals_num_days(days, session)
    event = (session.query(Event.id).
             filter(Event.id == 1).all())
    user_event = (session.query(UserEvent.id).
                  filter(UserEvent.event_id == 1).all())
    assert event == []
    assert user_event == []


def test_successful_undeleted_events(event_test_client, session, event):
    event_test_client.delete("/event/1")
    days = 20
    delete_events_after_optionals_num_days(days, session)
    event = session.query(Event.id).filter(Event.id == 1).all()
    user_event = session.query(UserEvent.id).filter(UserEvent.event_id == 1).all()
    assert event != []
    assert user_event != []
