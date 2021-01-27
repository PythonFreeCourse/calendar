import datetime
import functools
import frozendict
import requests
from typing import Dict, Tuple, Union

from app import config


# This feature requires an API KEY - get yours free @ www.weatherapi.com

SUCCESS_STATUS = 0
ERROR_STATUS = -1
ASTRONOMY_URL = "http://api.weatherapi.com/v1/astronomy.json"
NO_API_RESPONSE = "No response from server"


def freezeargs(func):
    """Transform mutable dictionary into immutable
    Credit to 'fast_cen' from 'stackoverflow'
    https://stackoverflow.com/questions/6358481/
    using-functools-lru-cache-with-dictionary-arguments
    """
    @functools.wraps(func)
    def wrapped(*args, **kwargs):
        args = tuple([frozendict.frozendict(arg)
                      if isinstance(arg, dict) else arg for arg in args])
        kwargs = {k: frozendict.frozendict(v) if isinstance(v, dict) else v
                  for k, v in kwargs.items()}
        return func(*args, **kwargs)
    return wrapped


@freezeargs
@functools.lru_cache(maxsize=128, typed=False)
def get_data_from_api(formatted_date: str, location: str)\
        -> Union[Tuple[None, str], Tuple[dict, None]]:
    """ get the relevant astronomical data by calling the "weather api" API.
    Args:
        formatted_date (date) - relevant date.
        location (str) - location name.
    Returns:
        response_json (json dict) - relevant part (data / error) of the
        JSON returned by the API.
        error_text (str) - error message.
    """
    input_query_string = dict(key=config.ASTRONOMY_API_KEY, q=location,
                              dt=formatted_date)
    try:
        response = requests.request("GET", ASTRONOMY_URL,
                                    params=input_query_string)
    except requests.exceptions.RequestException:
        return None, NO_API_RESPONSE
    if response.ok:
        try:
            return response.json()['location'], None
        except KeyError:
            return None, response.json()['error']['message']
    return None, NO_API_RESPONSE


def get_astronomical_data(requested_date: datetime.datetime, location: str)\
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
    output = {}
    formatted_date = requested_date.strftime('%Y-%m-%d')
    astronomical_data, error_text = get_data_from_api(formatted_date,
                                                      location)
    if astronomical_data:
        output["Status"] = SUCCESS_STATUS
        output.update(astronomical_data)
    else:
        output["Status"] = ERROR_STATUS
        output["ErrorDescription"] = error_text
    return output
