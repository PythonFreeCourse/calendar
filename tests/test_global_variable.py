REGISTER_DETAIL = {
    'username': 'correct_user', 'full_name': 'full_name',
    'password': 'correct_password', 'confirm_password': 'correct_password',
    'email': 'example@email.com', 'description': ""}

LOGIN_DATA = {'username': 'correct_user', 'password': 'correct_password'}


def test_global_var(global_var_test_client):
    response = global_var_test_client.get("/global-variable")

    assert response.ok
    assert b'correct_user' not in response.content
    assert b'Sign In' in response.content
    assert b'Sign Up' in response.content

    global_var_test_client.post(
        global_var_test_client.app.url_path_for('register'),
        data=REGISTER_DETAIL)
    global_var_test_client.post(
        global_var_test_client.app.url_path_for('login'),
        data=LOGIN_DATA)

    response = global_var_test_client.get("/global-variable")
    assert response.ok
    assert b'correct_user' in response.content
    assert b'Sign In' not in response.content
    assert b'Profile' in response.content
