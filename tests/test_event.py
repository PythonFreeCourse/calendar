from fastapi.testclient import TestClient

from app.main import app

client = TestClient(app)


def test_eventedit():
    response = client.get("/event/edit")
    assert response.status_code == 200
    assert b"Edit Event" in response.content


def test_eventview_with_id():
    response = client.get("/event/view/1")
    assert response.status_code == 200
    assert b"View Event" in response.content


def test_eventview_without_id():
    response = client.get("/event/view")
    assert response.status_code == 404
