from app.internal import jokes

def test_joke(client):
    resp = client.get('/joke')
    assert resp.ok
    assert resp.json


def test_get_a_joke(session, joke):
    assert jokes.have_a_joke(session).text == joke.text
