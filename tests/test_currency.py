CURRENCY = '/currency'
CUSTOM_DATE = "/2021-1-3"


def test_router_good(client):
    resp = client.get(CURRENCY)
    assert resp.ok
    resp = client.get(CURRENCY + CUSTOM_DATE)
    assert resp.ok
    assert b'Currency' in resp.content
