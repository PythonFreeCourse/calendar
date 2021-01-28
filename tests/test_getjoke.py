from app.routers import getjoke


def test_getjoke(client):
    resp = client.get('/getjoke')
    assert resp.ok
    assert resp.json
