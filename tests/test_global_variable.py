def test_global_var(global_var_test_client):
    response = global_var_test_client.get("/global-variable")
    assert response.ok
    assert b'test_user' in response.content
