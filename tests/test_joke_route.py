def test_joke(client):
    resp = client.get('/joke')
    assert resp.ok
    assert resp.json
