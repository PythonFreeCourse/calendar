from app.internal.currency import is_valid_currency_api_response
from fastapi import status


CURRENCY = '/currency'


def test_reponse_bad(requests_mock_bad):
    assert not is_valid_currency_api_response('')


def test_response_good(requests_mock_good):
    assert is_valid_currency_api_response('')


def test_response_error(requests_mock_error):
    assert not is_valid_currency_api_response('')


def test_router_good(client, requests_mock_good):
    resp = client.get(CURRENCY)
    assert resp.status_code == status.HTTP_200_OK
    assert b'Currency</a>' in resp.content


def test_router_bad(client, requests_mock_bad):
    resp = client.get(CURRENCY)
    assert b'Currency</a>' not in resp.content


def test_router_error(client, requests_mock_error):
    resp = client.get(CURRENCY)
    assert b'Currency</a>' not in resp.content
