from fastapi.testclient import TestClient
from starlette.status import HTTP_303_SEE_OTHER

from app.main import app

CORRECT_EVENT_FORM_DATA = {
    'title': 'test title',
    'start_date': '2021-01-28',
    'start_time': '15:59',
    'end_date': '2021-01-27',
    'end_time': '15:01',
    'location_type': 'vc_url',
    'location': 'https://us02web.zoom.us/j/875384596',
    'description': 'content',
    'color': 'red',
    'availability': 'busy',
    'privacy': 'public'
}

WRONG_EVENT_FORM_DATA = {
    'title': 'test title',
    'start_date': '2021-01-28',
    'start_time': '15:59',
    'end_date': '2021-01-27',
    'end_time': '15:01',
    'location_type': 'vc_url',
    'location': 'not a zoom link',
    'description': 'content',
    'color': 'red',
    'availability': 'busy',
    'privacy': 'public'
}

client = TestClient(app)


def test_eventedit():
    response = client.get("/event/edit")
    assert response.status_code == 200
    assert b"Edit Event" in response.content


def test_eventedit_post_correct(user):
    response = client.post("/event/edit", data=CORRECT_EVENT_FORM_DATA)
    assert response.status_code == HTTP_303_SEE_OTHER
    assert '/event/view/' in response.headers['location']


def test_eventedit_post_wrong(user):
    response = client.post("/event/edit", data=WRONG_EVENT_FORM_DATA)
    assert response.json()['detail'] == 'VC type with no valid zoom link'


def test_eventview_with_id():
    response = client.get("/event/view/1")
    assert response.status_code == 200
    assert b"View Event" in response.content


def test_eventview_without_id():
    response = client.get("/event/view")
    assert response.status_code == 404
