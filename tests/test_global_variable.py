from app.demos.global_variable import create_test_logged_user


def test_global_var(global_var_test_client, session):
    response = global_var_test_client.get("/global-variable")
    assert response.ok
    assert b'test_user' not in response.content
    assert b'Sign In' in response.content
    assert b'Sign Up' in response.content

    create_test_logged_user(session)
    response = global_var_test_client.get("/global-variable")
    assert response.ok
    assert b'test_user' in response.content
    assert b'Sign In' not in response.content
    assert b'Profile' in response.content
