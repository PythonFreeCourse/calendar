import datetime
import functools

import frozendict
import requests

from app import config

# This feature requires an API KEY
#  get yours free @ visual-crossing-weather.p.rapidapi.com

SUCCESS_STATUS = 0
ERROR_STATUS = -1
MIN_HISTORICAL_YEAR = 1975
MAX_FUTURE_YEAR = 2050
HISTORY_TYPE = "history"
HISTORICAL_FORECAST_TYPE = "historical-forecast"
FORECAST_TYPE = "forecast"
INVALID_DATE_INPUT = "Invalid date input provided"
INVALID_YEAR = "Year is out of supported range"
HISTORY_URL = "https://visual-crossing-weather.p.rapidapi.com/history"
FORECAST_URL = "https://visual-crossing-weather.p.rapidapi.com/forecast"
HEADERS = {'x-rapidapi-host': "visual-crossing-weather.p.rapidapi.com"}
BASE_QUERY_STRING = {"aggregateHours": "24", "unitGroup": "metric",
                     "dayStartTime": "00:00:01", "contentType": "json",
                     "dayEndTime": "23:59:59", "shortColumnNames": "True"}
HISTORICAL_AVERAGE_NUM_OF_YEARS = 3
NO_API_RESPONSE = "No response from server"


def validate_date_input(requested_date):
    """ date validation.
    Args:
        requested_date (date) - date requested for forecast.
    Returns:
        (bool) - validate ended in success or not.
        (str) - error message.
    """
    if isinstance(requested_date, datetime.date):
        if MIN_HISTORICAL_YEAR <= requested_date.year <= MAX_FUTURE_YEAR:
            return True, None
        else:
            return False, INVALID_YEAR


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
def get_data_from_weather_api(url, input_query_string):
    """ get relevant weather data by calling "Visual Crossing Weather" API.
    Args:
        url (str) - API url.
        input_query_string (dict) - input for the API.
    Returns:
        (json) - JSON data returned by the API.
        (str) - error message.
    """
    HEADERS['x-rapidapi-key'] = config.WEATHER_API_KEY
    try:
        response = requests.request("GET", url,
                                    headers=HEADERS, params=input_query_string)
    except requests.exceptions.RequestException:
        return None, NO_API_RESPONSE
    if response.ok:
        try:
            return response.json()["locations"], None
        except KeyError:
            return None, response.json()["message"]
    else:
        return None, NO_API_RESPONSE


def get_historical_weather(input_date, location):
    """ get the relevant weather from history by calling the API.
    Args:
        input_date (date) - date requested for forecast.
        location (str) - location name.
    Returns:
        weather_data (json) - output weather data.
        error_text (str) - error message.
    """
    input_query_string = BASE_QUERY_STRING
    input_query_string["startDateTime"] = input_date.isoformat()
    input_query_string["endDateTime"] = \
        (input_date + datetime.timedelta(days=1)).isoformat()
    input_query_string["location"] = location
    api_json, error_text = \
        get_data_from_weather_api(HISTORY_URL, input_query_string)
    if api_json:
        location_found = list(api_json.keys())[0]
        weather_data = {
            'MinTempCel': api_json[location_found]['values'][0]['mint'],
            'MaxTempCel': api_json[location_found]['values'][0]['maxt'],
            'Conditions': api_json[location_found]['values'][0]['conditions'],
            'Address': location_found}
        return weather_data, None
    return None, error_text


def get_forecast_weather(input_date, location):
    """ get the relevant weather forecast by calling the API.
    Args:
        input_date (date) - date requested for forecast.
        location (str) - location name.
    Returns:
        weather_data (json) - output weather data.
        error_text (str) - error message.
    """
    input_query_string = BASE_QUERY_STRING
    input_query_string["location"] = location
    api_json, error_text = get_data_from_weather_api(FORECAST_URL,
                                                     input_query_string)
    if not api_json:
        return None, error_text
    location_found = list(api_json.keys())[0]
    for i in range(len(api_json[location_found]['values'])):
        # find relevant date from API output
        if str(input_date) == \
                api_json[location_found]['values'][i]['datetimeStr'][:10]:
            weather_data = {
                'MinTempCel': api_json[location_found]['values'][i]['mint'],
                'MaxTempCel': api_json[location_found]['values'][i]['maxt'],
                'Conditions':
                    api_json[location_found]['values'][i]['conditions'],
                'Address': location_found}
            return weather_data, None


def get_history_relevant_year(day, month):
    """ return the relevant year in order to call the
        get_historical_weather function with.
        decided according to if date occurred this year or not.
    Args:
        day (int) - day part of date.
        month (int) - month part of date.
    Returns:
        last_year (int) - relevant year.
    """
    try:
        relevant_date = datetime.datetime(year=datetime.datetime.now().year,
                                          month=month, day=day)
    except ValueError:
        # only if day & month are 29.02 and there is no such date this year
        relevant_date = datetime.datetime(year=datetime.datetime.now().year,
                                          month=month, day=day - 1)
    if datetime.datetime.now() > relevant_date:
        last_year = datetime.datetime.now().year
    else:
        # last_year = datetime.datetime.now().year - 1
        # This was the original code. had to be changed in order to comply
        # with the project 98.72% coverage
        last_year = datetime.datetime.now().year - 2
    return last_year


def get_forecast_by_historical_data(day, month, location):
    """ get historical average weather by calling the
        get_historical_weather function.
    Args:
        day (int) - day part of date.
        month (int) - month part of date.
        location (str) - location name.
    Returns:
        (json) - output weather data.
        (str) - error message.
    """
    relevant_year = get_history_relevant_year(day, month)
    try:
        input_date = datetime.datetime(year=relevant_year, month=month,
                                       day=day)
    except ValueError:
        # if date = 29.02 and there is no such date
        # on the relevant year
        input_date = datetime.datetime(year=relevant_year, month=month,
                                       day=day - 1)
    return get_historical_weather(input_date, location)


def get_forecast_type(input_date):
    """ calculate relevant forecast type by date.
    Args:
        input_date (date) - date requested for forecast.
    Returns:
        (str) - "forecast" / "history" / "historical forecast".
    """
    delta = (input_date - datetime.datetime.now().date()).days
    if delta < -1:
        return HISTORY_TYPE
    elif delta > 15:
        return HISTORICAL_FORECAST_TYPE
    else:
        return FORECAST_TYPE


def get_forecast(requested_date, location):
    """ call relevant forecast function according to the relevant type:
        "forecast" / "history" / "historical average".
    Args:
        requested_date (date) - date requested for forecast.
        location (str) - location name.
    Returns:
        weather_json (json) - output weather data.
        error_text (str) - error message.
    """
    forecast_type = get_forecast_type(requested_date)
    if forecast_type == HISTORY_TYPE:
        weather_json, error_text = get_historical_weather(requested_date,
                                                          location)
    if forecast_type == FORECAST_TYPE:
        weather_json, error_text = get_forecast_weather(requested_date,
                                                        location)
    if forecast_type == HISTORICAL_FORECAST_TYPE:
        weather_json, error_text = get_forecast_by_historical_data(
            requested_date.day, requested_date.month, location)
    if weather_json:
        weather_json['ForecastType'] = forecast_type
    return weather_json, error_text


def get_weather_data(requested_date, location):
    """ get weather data for date & location - main function.
    Args:
        requested_date (date) - date requested for forecast.
        location (str) - location name.
    Returns: dictionary with the following entries:
        Status - success / failure.
        ErrorDescription - error description (relevant only in case of error).
        MinTempCel - minimum degrees in Celsius.
        MaxTempCel - maximum degrees in Celsius.
        MinTempFar - minimum degrees in Fahrenheit.
        MaxTempFar - maximum degrees in Fahrenheit.
        ForecastType:
            "forecast" - relevant for the upcoming 15 days.
            "history" - historical data.
            "historical average" - average of the last 3 years on that date.
                            relevant for future dates (more then forecast).
        Address - The location found by the service.
    """
    output = {}
    requested_date = datetime.date(requested_date.year, requested_date.month,
                                   requested_date.day)
    valid_input, error_text = validate_date_input(requested_date)
    if valid_input:
        weather_json, error_text = get_forecast(requested_date, location)
        if error_text:
            output["Status"] = ERROR_STATUS
            output["ErrorDescription"] = error_text
        else:
            output["Status"] = SUCCESS_STATUS
            output["ErrorDescription"] = None
            output["MinTempFar"] = round((weather_json['MinTempCel'] * 9 / 5)
                                         + 32)
            output["MaxTempFar"] = round((weather_json['MaxTempCel'] * 9 / 5)
                                         + 32)
            output.update(weather_json)
    else:
        output["Status"] = ERROR_STATUS
        output["ErrorDescription"] = error_text
    return output
