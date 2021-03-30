import pytest
from starlette.status import HTTP_302_FOUND


def test_register_route_ok(client):
    response = client.get("/register")
    assert response.ok


REGISTER_FORM_VALIDATORS = [
    ('ad', 'admin_user', 'password', 'password', 'example@mail.com',
        'description', b'Username must contain'),
    ('admin', 'admin_user', 'pa', 'pa', 'example@mail.com',
        'description', b'Password must contain'),
    ('admin', 'admin_user', 'password', 'wrong_password', 'example@mail.com',
        'description', b"match"),
    ('admin', 'admin_user', 'password', 'password', 'invalid_mail',
        'description', b"Email address is not valid"),
    ('', 'admin_user', 'password', 'password', 'example@mail.com',
        'description', b'Username field is required'),
    ('admin', '', 'password', 'password', 'example@mail.com',
        'description', b'Full_name field is required'),
    ('admin', 'admin_user', '', 'password', 'example@mail.com',
        'description', b'Password field is required'),
    ('admin', 'admin_user', 'password', '', 'example@mail.com',
        'description', b'Confirm_password field is required'),
    ('admin', 'admin_user', 'password', 'password', '',
        'description', b'Email field is required'),
    ]


"""
Test all active pydantic validators
"""


@pytest.mark.parametrize(
    "username, full_name, password, confirm_password, email, description,"
    + "expected_response", REGISTER_FORM_VALIDATORS)
def test_register_form_validators(
    client, username, full_name, password, confirm_password,
        email, description, expected_response):
    data = {
        'username': username, 'full_name': full_name,
        'password': password, 'confirm_password': confirm_password,
        'email': email, 'description': description}
    data = client.post('/register', data=data).content
    assert expected_response in data


"""
Test successfully register user to database, after passing all validators
"""


def test_register_successfull(session, security_test_client):
    data = {'username': 'username', 'full_name': 'full_name',
            'password': 'password', 'confirm_password': 'password',
            'email': 'example@email.com', 'description': ""}
    data = security_test_client.post('/register', data=data)
    assert data.status_code == HTTP_302_FOUND


UNIQUE_FIELDS_ARE_TAKEN = [
    ('admin', 'admin_user', 'password', 'password', 'example_new@mail.com',
        'description', b'That username is already taken'),
    ('admin_new', 'admin_user', 'password', 'password', 'example@mail.com',
        'description', b"Email already registered")
    ]


"""
Test register a user fails due to unique database fields already in use
"""


@pytest.mark.parametrize(
    "username, full_name, password, confirm_password,"
    + "email, description, expected_response", UNIQUE_FIELDS_ARE_TAKEN)
def test_unique_fields_are_taken(
        session, security_test_client, username,
        full_name, password, confirm_password,
        email, description, expected_response):
    user_data = {
        'username': 'username', 'full_name': 'full_name',
        'password': 'password', 'confirm_password': 'password',
        'email': 'example@email.com', 'description': ""}
    security_test_client.post('/register', data=user_data)
    data = security_test_client.post('/register', data=user_data).content
    assert expected_response in data
