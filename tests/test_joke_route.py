def test_joke(client, session):
    resp = client.get('/joke')
    assert resp.ok
    assert resp.json
