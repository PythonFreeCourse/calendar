
def test_ok(client):
    resp = client.get('/weight')
    assert resp.ok
    assert b"Weight" in resp.content


def test_post_ok(client, user):
    new_data = {'target': user.target_weight, 'current_weight': 60}
    resp = client.post('/weight/', data=new_data)
    assert resp.ok
