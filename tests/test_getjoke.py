def test_getjoke(client):
    resp = client.get('/getjoke')
    assert resp.ok
    assert resp.json
