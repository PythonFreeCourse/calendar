import fastapi


def test_home(client):
    response = client.get("/")
    assert response.status_code == fastapi.status.HTTP_200_OK
