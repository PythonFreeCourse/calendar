from app.internal.notes import notes
from starlette.testclient import TestClient
import json
import pytest


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


def test_update_note(notes_test_client: TestClient, monkeypatch):
    test_update_data = {
        "id": 1, "title": "someone",
        "description": "someone else", "timestamp": None}

    async def mock_get(session, id):
        return True

    monkeypatch.setattr(notes, "get", mock_get)

    async def mock_put(session, id, payload):
        return 1

    monkeypatch.setattr(notes, "put", mock_put)

    response = notes_test_client.put(
        "/notes/1/", data=json.dumps(test_update_data))
    assert response.status_code == 200
    assert response.json() == test_update_data


@pytest.mark.parametrize(
    "id, payload, status_code",
    [
        [1, {}, 422],
        [1, {"description": "bar"}, 422],
        [999, {"title": "foo", "description": "bar"}, 404],
    ],
)
def test_update_note_invalid(notes_test_client: TestClient,
                             monkeypatch, id, payload, status_code):
    async def mock_get(session, id):
        return None

    monkeypatch.setattr(notes, "get", mock_get)

    response = notes_test_client.put(
        f"/notes/{id}/", data=json.dumps(payload),)
    assert response.status_code == status_code


def test_delete_note(notes_test_client: TestClient, monkeypatch):
    test_data = {
        "id": 1, "title": "something",
        "description": "something else", "timestamp": None}

    async def mock_get(session, id):
        return test_data

    monkeypatch.setattr(notes, "get", mock_get)

    async def mock_delete(session, id):
        return id

    monkeypatch.setattr(notes, "delete", mock_delete)

    response = notes_test_client.delete("/notes/1/")
    assert response.status_code == 200
    assert response.json() == test_data


def test_delete_note_incorrect_id(notes_test_client: TestClient, monkeypatch):
    async def mock_get(session, id):
        return None

    monkeypatch.setattr(notes, "get", mock_get)

    response = notes_test_client.delete("/notes/999/")
    assert response.status_code == 404
    assert response.json()["detail"] == "Note not found"
