from app.routers.cursor import get_cursor_settings, get_user, router

CURSOR_SETTINGS_URL = router.url_path_for("cursor_settings")
GET_CHOICES_URL = router.url_path_for("get_cursor_choices")
LOAD_CURSOR_URL = router.url_path_for("load_cursor")
OK = 200


def test_get_cursor_settings(settings_test_client):
    response = settings_test_client.get(
        url=CURSOR_SETTINGS_URL)
    assert response.ok
    assert b"Cursor Settings" in response.content


def test_cursor_choices(session, settings_test_client):
    data = {
        "primary_cursor": "arrow",
        "secondary_cursor": "p1",
    }
    first_response = settings_test_client.post(
        url=GET_CHOICES_URL, data=data)
    primary1, secondary1 = get_cursor_settings(session, user_id=1)

    data["secondary_cursor"] = "default"
    second_response = settings_test_client.post(
        url=GET_CHOICES_URL, data=data)
    primary2, secondary2 = get_cursor_settings(session, user_id=1)

    assert first_response.ok and second_response.ok
    assert primary1 == "arrow" and secondary1 == "p1"
    assert primary2 == "arrow" and secondary2 == "default"


def test_load_cursor(session, settings_test_client):
    data = {
        "primary_cursor": "cloud",
        "secondary_cursor": "ice",
    }
    response = settings_test_client.post(
        url=GET_CHOICES_URL, data=data)
    response = settings_test_client.get(
        url=LOAD_CURSOR_URL)

    primary_cursor, secondary_cursor = get_cursor_settings(session, user_id=1)
    assert response.ok
    assert primary_cursor == "cloud" and secondary_cursor == "ice"


def test_get_user(session, user):
    new_user = get_user(session, "does_not_exist", user)
    assert new_user.username == user.username
