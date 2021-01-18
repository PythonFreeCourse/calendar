from fastapi.testclient import TestClient

from app.main import app

client = TestClient(app)


def test_eventedit():
    response = client.get("/event/edit")
    assert response.status_code == 200
    assert b"Edit Event" in response.content
