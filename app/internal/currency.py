from typing import Dict

import requests


def is_valid_currency_api_response(date: str) -> bool:
    """Checks for valid response from the currency-API request (returns bool)"""

    try:
        response = requests.get(f'https://api.exchangeratesapi.io/{date}')
    except requests.ConnectionError:
        # TODO: Log error to log file
        return False
    else:
        return response.status_code == 200
