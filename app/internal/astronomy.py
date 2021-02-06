import asyncio
import datetime
import functools
import httpx
from typing import Dict

from app import config


# This feature requires an API KEY - get yours free @ www.weatherapi.com

ASTRONOMY_URL = "http://api.weatherapi.com/v1/astronomy.json"
NO_API_RESPONSE = "No response from server"


@functools.lru_cache(maxsize=128, typed=False)
async def get_data_from_api(formatted_date: str, location: str)\
        -> Dict[str, int]:
    """ get the relevant astronomical data by calling the "weather api" API.
    Args:
        formatted_date (date) - relevant date.
        location (str) - location name.
    Returns:
        response_json (json dict) including:
        relevant part (data / error) of the JSON returned by the API.
        Success (bool)
        ErrorDescription (str) - error message.
    """
    input_query_string = {'key': config.ASTRONOMY_API_KEY, 'q': location,
                          'dt': formatted_date}
    output = {}
    try:
        async with httpx.AsyncClient() as client:
            response = await client.get(ASTRONOMY_URL,
                                        params=input_query_string)
    except httpx.HTTPError:
        output["Success"] = False
        output["ErrorDescription"] = NO_API_RESPONSE
        return output
    if response.status_code != httpx.codes.OK:
        output["Success"] = False
        output["ErrorDescription"] = NO_API_RESPONSE
        return output
    output["Success"] = True
    try:
        output.update(response.json()['location'])
        return output
    except KeyError:
        output["Success"] = False
        output["ErrorDescription"] = response.json()['error']['message']
        return output


async def get_astronomical_data(requested_date: datetime.datetime, location: str)\
        -> Dict[str, int]:
    """ get astronomical data (Sun & Moon) for date & location -
        main function.
    Args:
        requested_date (date) - date requested for astronomical data.
        location (str) - location name.
    Returns: dictionary with the following entries:
        Status - success / failure.
        ErrorDescription - error description (relevant only in case of error).
        location - relevant location values(relevant only in case of success).
            name, region, country, lat, lon etc.
        astronomy - relevant astronomy values, all time in local time -
            (relevant only in case of success):
            sunrise, sunset, moonrise, moonset, moon_phase, moon_illumination.
    """
    formatted_date = requested_date.strftime('%Y-%m-%d')
    return await get_data_from_api(formatted_date, location)
