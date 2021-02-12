from app.internal.notes import notes
from starlette.testclient import TestClient
import json


def test_create_note(notes_test_client: TestClient, monkeypatch):
    test_request_payload = {
        "title": "something", "description": "something else"
    }
    test_response_payload = {
        "id": 1, "title": "something", "description": "something else",
        "timestamp": None
    }

    async def mock_post(session, payload):
        return 1

    monkeypatch.setattr(notes, "post", mock_post)

    response = notes_test_client.post(
        "/notes/", data=json.dumps(test_request_payload),)

    assert response.status_code == 201
    assert response.json() == test_response_payload


def test_create_note_invalid_json(notes_test_client: TestClient):
    response = notes_test_client.post(
        "/notes/", data=json.dumps({"titles": "something"}))
    assert response.status_code == 422


def test_read_note(notes_test_client: TestClient, monkeypatch):
    test_data = {
        "title": "something", "description": "something else",
        "timestamp": None
    }

    async def mock_get(session, id):
        return test_data

    monkeypatch.setattr(notes, "get", mock_get)

    response = notes_test_client.get("/notes/1")
    assert response.status_code == 200
    assert response.json() == test_data


def test_read_note_incorrect_id(notes_test_client: TestClient, monkeypatch):
    async def mock_get(session, id):
        return None

    monkeypatch.setattr(notes, "get", mock_get)

    response = notes_test_client.get("/notes/999")
    assert response.status_code == 404
    assert response.json()["detail"] == "Note not found"


def test_read_all_notes(notes_test_client: TestClient, monkeypatch):
    test_data = [
        {"id": 1, "title": "something",
            "description": "something else", "timestamp": None},
        {"id": 2, "title": "someone",
         "description": "someone else", "timestamp": None},
    ]

    async def mock_get_all(session):
        return test_data

    monkeypatch.setattr(notes, "get_all", mock_get_all)

    response = notes_test_client.get("/notes/")
    assert response.status_code == 200
    assert response.json() == test_data
