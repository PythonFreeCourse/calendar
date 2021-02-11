from app.routers.notes import crud
from starlette.testclient import TestClient
import json


def test_create_note(notes_test_client: TestClient, monkeypatch):
    test_request_payload = {"title": "something",
                            "description": "something else"}
    test_response_payload = {
        "id": 1, "title": "something", "description": "something else"}

    async def mock_post(session, payload):
        return 1

    monkeypatch.setattr(crud, "post", mock_post)

    response = notes_test_client.post(
        "/notes/", data=json.dumps(test_request_payload),)

    assert response.status_code == 201
    assert response.json() == test_response_payload


def test_create_note_invalid_json(notes_test_client: TestClient):
    response = notes_test_client.post(
        "/notes/", data=json.dumps({"title": "something"}))
    assert response.status_code == 422
