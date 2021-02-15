def test_about_page(client):
    response = client.get("/about")
    assert response.ok
    assert b"Yam" in response.content
