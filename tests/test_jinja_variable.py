REGISTER_DETAIL = {
    "username": "correct_user",
    "full_name": "full_name",
    "password": "correct_password",
    "confirm_password": "correct_password",
    "email": "example@email.com",
    "description": "",
}

LOGIN_DATA = {"username": "correct_user", "password": "correct_password"}


def test_user_not_logged_in(security_test_client):
    response = security_test_client.get("/about")
    assert b"Sign Out" not in response.content
    assert b"Sign In" in response.content


def test_user_is_logged_in(security_test_client):
    security_test_client.post(
        security_test_client.app.url_path_for("register"),
        data=REGISTER_DETAIL,
    )
    security_test_client.post(
        security_test_client.app.url_path_for("login"),
        data=LOGIN_DATA,
    )
    response = security_test_client.get("/about")
    assert b"Sign Out" in response.content
    assert b"Sign In" not in response.content
