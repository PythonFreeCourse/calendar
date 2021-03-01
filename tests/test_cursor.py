from app.internal.security.dependencies import current_user
from app.routers.cursor import get_cursor_settings, router
from tests.test_login import test_login_successfull

CURSOR_SETTINGS_URL = router.url_path_for("cursor_settings")
GET_CHOICES_URL = router.url_path_for("get_cursor_choices")
LOAD_CURSOR_URL = router.url_path_for("load_cursor")


def test_get_cursor_settings(session, cursor_test_client):
    test_login_successfull(session, cursor_test_client)
    response = cursor_test_client.get(url=CURSOR_SETTINGS_URL)
    assert response.ok
    assert b"Cursor Settings" in response.content


def test_cursor_choices(session, cursor_test_client):
    test_login_successfull(session, cursor_test_client)
    data = {
        "primary_cursor": "arrow",
        "secondary_cursor": "sword",
        "user": current_user,
    }
    first_response = cursor_test_client.post(url=GET_CHOICES_URL, data=data)
    primary1, secondary1 = get_cursor_settings(session, user_id=1)

    data["secondary_cursor"] = "default"
    second_response = cursor_test_client.post(url=GET_CHOICES_URL, data=data)
    primary2, secondary2 = get_cursor_settings(session, user_id=1)

    assert first_response.ok and second_response.ok
    assert primary1 == "arrow" and secondary1 == "sword"
    assert primary2 == "arrow" and secondary2 == "default"


def test_load_cursor(session, cursor_test_client):
    data = {
        "primary_cursor": "fire",
        "secondary_cursor": "ice",
    }
    response = cursor_test_client.post(url=GET_CHOICES_URL, data=data)
    response = cursor_test_client.get(url=LOAD_CURSOR_URL)

    primary_cursor, secondary_cursor = get_cursor_settings(session, user_id=1)
    assert response.ok
    assert primary_cursor == "fire" and secondary_cursor == "ice"
