from fastapi.testclient import TestClient

from app.main import app, add_countries_to_db


client = TestClient(app)


def test_global_time_feature_opening():
    response = client.get("/global_time")
    assert response.status_code == 200
    assert b"Icons" in response.content


def test_global_time_choose_country(session):
    response = client.get("/global_time/choose")
    assert response.status_code == 200


def test_global_time_chosen_country_and_time_fails_without_ip(session):
    add_countries_to_db()
    country = 'Israel, Jerusalem'
    datetime = '2021-02-10 19:00:00'
    response = client.get(f"/global_time/{country}/{datetime}")
    assert response.status_code == 404


def test_global_time_chosen_country_and_time_with_valid_ip(session):
    add_countries_to_db()
    country = 'Israel, Jerusalem'
    datetime = '2021-02-10 19:00:00'
    valid_ip = '85.250.214.253'
    response = client.get(f"/global_time/{country}/{datetime}/{valid_ip}")
    assert response.status_code == 200


def test_global_time_chosen_country_and_time_with_invalid_ip(session):
    add_countries_to_db()
    country = 'Israel, Jerusalem'
    datetime = '2021-02-10 19:00:00'
    invalid_ip = '127.0.0.1'
    response = client.get(f"/global_time/{country}/{datetime}/{invalid_ip}")
    assert response.status_code == 200
    assert b"not associated" in response.content
