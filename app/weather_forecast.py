from datetime import datetime, timedelta
from dotenv import load_dotenv
from os import getenv
import requests


""" This feature requires an API KEY - get yours free @ visual-crossing-weather.p.rapidapi.com """

SUCCESS_STATUS = 0
ERROR_STATUS = -1
HISTORY_TYPE = "history"
HISTORICAL_AVERAGE_TYPE = "historical-average"
FORECAST_TYPE = "forecast"
HISTORY_URL = "https://visual-crossing-weather.p.rapidapi.com/history"
FORECAST_URL = "https://visual-crossing-weather.p.rapidapi.com/forecast"
HEADERS = {
    'x-rapidapi-host': "visual-crossing-weather.p.rapidapi.com"
    }
BASE_QUERY_STRING = {"aggregateHours": "24", "unitGroup": "metric", "dayStartTime": "00:00:01",
                     "contentType": "json", "dayEndTime": "23:59:59", "shortColumnNames": "True"}
HISTORICAL_AVERAGE_NUM_OF_YEARS = 3
OUTPUT = {"Status": SUCCESS_STATUS, "ErrorDescription": None, "MinTempCel": None, "MaxTempCel": None,
          "MinTempFar": None, "MaxTempFar": None, "Conditions": None, "ForecastType": None}


def validate_date_input(day, month, year):
    """ date validation.
    Args:
        day (int / str) - day part of date.
        month (int / str) - month part of date.
        year (int / str) - year part of date.
    Returns:
        (bool) - validate ended in success or not.
        day (int) - day part of date.
        month (int) - month part of date.
        year (int) - year part of date.
    """
    try:
        day = int(day)
        month = int(month)
        year = int(year)
    except ValueError:
        return False, day, month, year
    if 1975 <= year <= 2050:
        try:
            datetime(year=year, month=month, day=day)
        except ValueError:
            return False, day, month, year
    else:
        return False, day, month, year
    return True, day, month, year


def get_data_from_api(url, input_query_string):
    """ get the relevant weather data by calling the "Visual Crossing Weather" API.
    Args:
        url (str) - API url.
        input_query_string (dict) - input for the API.
    Returns:
        success_in_get_weather_data (bool) - did the API call ended in success or failure (location not found etc).
        response_json (json dict) - relevant part (data / error) of the JSON returned by the API.
    """
    load_dotenv()
    HEADERS['x-rapidapi-key'] = getenv('WEATHER_API_KEY')
    success_in_get_weather_data = True
    response = requests.request("GET", url, headers=HEADERS, params=input_query_string)
    try:
        response_json = response.json()["locations"]
    except KeyError:
        success_in_get_weather_data = False
        response_json = response.json()
    return success_in_get_weather_data, response_json


def get_historical_weather(input_date, location):
    """ get the relevant weather from history by calling the API.
    Args:
        input_date (date) - day part of date.
        location (str) - location name.
    Returns:
        (int) - minimum degrees in Celsius.
        (int) - maximum degrees in Celsius.
        (str) - weather conditions.
        (str) - location / error description.
    """
    input_query_string = BASE_QUERY_STRING
    input_query_string["startDateTime"] = input_date.isoformat()
    input_query_string["endDateTime"] = (input_date + timedelta(days=1)).isoformat()
    input_query_string["location"] = location
    success_in_get_weather_data, api_json = get_data_from_api(HISTORY_URL, input_query_string)
    if success_in_get_weather_data:
        for item in api_json:
            # print("historical:", api_json[item]['values'][0]['mint'], api_json[item]['values'][0]['maxt'])
            min_temp = api_json[item]['values'][0]['mint']
            max_temp = api_json[item]['values'][0]['maxt']
            conditions = api_json[item]['values'][0]['conditions']
        return min_temp, max_temp, conditions, api_json[item]['address']
    else:
        return None, None, None, api_json['message']


def get_forecast_weather(input_date, location):
    """ get the relevant weather forecast by calling the API.
    Args:
        input_date (date) - day part of date.
        location (str) - location name.
    Returns:
        (int) - minimum degrees in Celsius.
        (int) - maximum degrees in Celsius.
        (str) - weather conditions.
        (str) - location / error description.
    """
    input_query_string = BASE_QUERY_STRING
    input_query_string["location"] = location
    success_in_get_weather_data, api_json = get_data_from_api(FORECAST_URL, input_query_string)
    if success_in_get_weather_data:
        for item in api_json:
            for i in range(len(api_json[item]['values'])):
                if input_date == datetime.fromisoformat(api_json[item]['values'][i]['datetimeStr'][:-6]):
                    min_temp = api_json[item]['values'][i]['mint']
                    max_temp = api_json[item]['values'][i]['maxt']
                    conditions = api_json[item]['values'][i]['conditions']
        return min_temp, max_temp, conditions, api_json[item]['address']
    else:
        return None, None, None, api_json['message']


def get_relevant_years_for_historical_average(day, month):
    """ get a list for relevant years to call the get_historical_weather function
        according to if date occurred this year or not.
    Args:
        day (int) - day part of date.
        month (int) - month part of date.
    Returns:
        (list) - relevant years range.
    """
    if datetime.now() > datetime(year=datetime.now().year, month=month, day=day):
        last_year = datetime.now().year
    else:
        last_year = datetime.now().year - 1
    return list(range(last_year, last_year - HISTORICAL_AVERAGE_NUM_OF_YEARS, -1))


def get_historical_average_weather(day, month, location):
    """ get historical average weather by calling the get_historical_weather function
        several times and calculate average.
    Args:
        day (int) - day part of date.
        month (int) - month part of date.
        location (str) - location name.
    Returns:
        (int) - minimum average degrees in Celsius.
        (int) - maximum average degrees in Celsius.
        (str) - location / error description.
    """
    sum_min = 0
    sum_max = 0
    if day == 29 and month == 2:
        day = 28
    relevant_years = (get_relevant_years_for_historical_average(day, month))
    for relevant_year in relevant_years:
        input_date = datetime(year=relevant_year, month=month, day=day)
        min_temp, max_temp, conditions, description = get_historical_weather(input_date, location)
        if min_temp is not None:
            sum_min += min_temp
            sum_max += max_temp
    if min_temp is not None:
        return sum_min / HISTORICAL_AVERAGE_NUM_OF_YEARS, sum_max / HISTORICAL_AVERAGE_NUM_OF_YEARS, description
    else:
        return None, None, description


def calculate_forecast_type(input_date):
    """ calculate relevant forecast type by date.
    Args:
        input_date (date) - day part of date.
    Returns:
        output_type (str) - "forecast" / "history" / "historical average".
    """
    delta = (input_date - datetime.now()).days
    if delta < -1:
        output_type = HISTORY_TYPE
    elif delta > 15:
        output_type = HISTORICAL_AVERAGE_TYPE
    else:
        output_type = FORECAST_TYPE
    return output_type


def get_forecast(day, month, year, location):
    """ call relevant forecast function according to the relevant type:
        "forecast" / "history" / "historical average".
    Args:
        day (int) - day part of date.
        month (int) - month part of date.
        year (int) - year part of date.
        location (str) - location name.
    Returns:
        ForecastType (str):
            "forecast" - relevant for the upcoming 15 days.
            "history" - historical data.
            "historical average" - average of the last 3 years on that date.
                                    relevant for future dates (more then forecast).
        min_temp (int) - minimum degrees in Celsius.
        max_temp (int) - maximum degrees in Celsius.
        conditions (str) - weather conditions.
        Description (str) - location / error description.
    """
    input_date = datetime(year=year, month=month, day=day)
    forecast_type = calculate_forecast_type(input_date)
    if forecast_type == HISTORY_TYPE:
        min_temp, max_temp, conditions, description = get_historical_weather(input_date, location)
    if forecast_type == FORECAST_TYPE:
        min_temp, max_temp, conditions, description = get_forecast_weather(input_date, location)
    if forecast_type == HISTORICAL_AVERAGE_TYPE:
        min_temp, max_temp, description = get_historical_average_weather(day, month, location)
        conditions = ""
    return forecast_type, min_temp, max_temp, conditions, description


def get_weather_data(day, month, year, location):
    """ get weather data for date & location - main function.
    Args:
        day (int / str) - day part of date.
        month (int / str) - month part of date.
        year (int / str) - year part of date.
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
    output = OUTPUT
    valid_input, day, month, year = validate_date_input(day, month, year)
    if valid_input:
        forecast_type, min_temp, max_temp, conditions, description = get_forecast(day, month, year, location)
        if min_temp is None:
            output["Status"] = ERROR_STATUS
            output["ErrorDescription"] = description
        else:
            output["Status"] = SUCCESS_STATUS
            output["MinTempCel"] = round(min_temp)
            output["MaxTempCel"] = round(max_temp)
            output["MinTempFar"] = round((min_temp * 9/5) + 32)
            output["MaxTempFar"] = round((max_temp * 9/5) + 32)
            output["Conditions"] = conditions
            output["ForecastType"] = forecast_type
            output["Address"] = description
    else:
        output["Status"] = ERROR_STATUS
        output["ErrorDescription"] = "Invalid date input provided"
    return output


if __name__ == "__main__":
    print(get_weather_data("29", "02", 2024, "tel aviv"))
