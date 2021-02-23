from datetime import datetime
import functools
from typing import Any, Dict

import httpx

from app import config

# This feature requires an API key. Get yours free at www.weatherapi.com.
ASTRONOMY_URL = "https://api.weatherapi.com/v1/astronomy.json"
NO_API_RESPONSE = _("No response from server.")


async def get_astronomical_data(
        date: datetime, location: str
) -> Dict[str, Any]:
    """Returns astronomical data (sun and moon) for date and location.

    Args:
        date: The requested date for astronomical data.
        location: The location name.

    Returns:
        A dictionary with the following entries:
            success: True or False.
            error: The error description.
            location: A dictionary of relevant data, including:
                name, region, country, lat, lon etc.
            astronomy: A dictionary of relevant data, including:
                sunrise, sunset, moonrise, moonset, moon_phase, and
                moon_illumination.
    """
    formatted_date = date.strftime('%Y-%m-%d')
    return await _get_astronomical_data_from_api(formatted_date, location)


@functools.lru_cache(maxsize=128)
async def _get_astronomical_data_from_api(
        date: str, location: str
) -> Dict[str, Any]:
    """Returns astronomical_data from a Weather API call.

    Args:
        date: The requested date for astronomical data.
        location: The location name.

    Returns:
        A dictionary with the results from the API call.
    """
    input_query_string = {
        'key': config.ASTRONOMY_API_KEY,
        'q': location,
        'dt': date,
    }

    output: Dict[str, Any] = {}
    try:
        async with httpx.AsyncClient() as client:
            response = await client.get(
                ASTRONOMY_URL, params=input_query_string)
    except httpx.HTTPError:
        output["success"] = False
        output["error"] = NO_API_RESPONSE
        return output

    if response.status_code != httpx.codes.OK:
        output["success"] = False
        output["error"] = NO_API_RESPONSE
        return output

    output["success"] = True
    try:
        output.update(response.json()['location'])
        return output
    except KeyError:
        output["success"] = False
        output["error"] = response.json()['error']['message']
        return output
