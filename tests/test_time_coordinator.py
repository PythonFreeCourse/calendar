# from datetime import datetime

# from app.resources.countries import countries
# from app.internal.event import (
#     add_countries_to_db, get_all_countries_names,
#     get_meeting_local_duration
# )


# def test_get_all_countries_names(session):
#     countries_num = 0
#     for country in countries:
#         for timezone in country['timezones']:
#             countries_num += 1
#     function_result = len(get_all_countries_names(session))
#     assert countries_num == function_result


# def test_time_convertion(session):
#     add_countries_to_db(session)
#     timezone = 'Asia/Jerusalem'
#     country_to_convert_to = "France, Paris"
#     start = datetime(year=2021, month=2, day=2, hour=14, minute=0)
#     end = datetime(year=2021, month=2, day=2, hour=15, minute=0)
#     converted = get_meeting_local_duration(
#         start, end, timezone, country_to_convert_to, session
#     )
#     assert converted == '13:00 - 14:00'
