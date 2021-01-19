from fastapi.testclient import TestClient
from datetime import datetime
from app.main import app
from app.routers.event import prepre_mail_for_update_event
from app.database.models import Event

client = TestClient(app)


def test_eventedit():
    response = client.get("/event/edit")
    assert response.status_code == 200
    assert b"Edit Event" in response.content

def test_update_event(session, event):
    data = {'event_id': event.id,
            'event_title':event.title,
            'from_date': event.start,
            'to_date': datetime.now(),
            'content': event.content,
            'db': session,
    }
    assert client.post('event/1/edit', data=data).status_code == 200
    assert b'Error' in client.post('event/1/edit', data=data).content
def test_update_event2(session, event):
    data = {'event_id': event.id,
            'event_title':event.title,
            'from_date': event.end,
            'to_date': event.start,
            'content': event.content,
            'db': session,
    }
    assert client.post('event/1/edit', data=data).status_code == 200
    assert b'date' in client.post('event/1/edit', data=data).content
def test_update_event3(session, event):
    data = {'event_id': event.id,
            'event_title':event.title,
            'from_date': event.start,
            'to_date': datetime.now(),
            'content': event.content,
            'db': None,
    }
    assert client.post('event/1/edit', data=data).status_code == 200
    assert b'Error' in client.post('event/1/edit', data=data).content

def test_prepre_email(event):
    new_event = Event(
            title=event.title + '1',
            start=event.end,
            end=event.start,
            content=event.content+'1')
    link = 'test'
    assert 'changed' in prepre_mail_for_update_event(event, new_event, link)[1]
    assert 'updated' in prepre_mail_for_update_event(event, new_event, link)
