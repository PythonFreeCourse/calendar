from datetime import datetime, timedelta

import pytest

from app.database.models import SalarySettings
from app.routers.salary import config, utils


NIGHT_TIMES = [
    (datetime(2020, 1, 15), False,
     (datetime(2020, 1, 15, config.NIGHT_START),
      datetime(2020, 1, 16, config.NIGHT_END))),
    (datetime(2020, 1, 15), True,
     (datetime(2020, 1, 14, config.NIGHT_START),
      datetime(2020, 1, 15, config.NIGHT_END)))
]


NIGHT_SHIFTS = [
    (datetime(2020, 12, 1, 23, 15), datetime(2020, 12, 1, 5, 15), False),  # Invalid shift
    (datetime(2020, 12, 1, 9, 15), datetime(2020, 12, 1, 18, 15), False),  # Not during night
    (datetime(2020, 12, 1, 2020, 15), datetime(2020, 12, 1, 23, 15), False),  # Too short - evening
    (datetime(2020, 12, 1, 5, 15), datetime(2020, 12, 1, 6, 15), False),  # Too short - morning
    (datetime(2020, 12, 1, 3, 15), datetime(2020, 12, 1, 7, 15), True),  # Same Date 
    (datetime(2020, 12, 1, 19, 15), datetime(2020, 12, 2, 1, 15), True),  # Date changing
    (datetime(2020, 12, 1, 19, 15), datetime(2020, 12, 2, 7, 15), True)  # Entire night
]


@pytest.fixture()
def wage():
    return SalarySettings(user_id=1, category_id=1, wage=30)


def test_get_shift_len():
    start = datetime(2020, 1, 1, 1)
    end = start + timedelta(hours=1)
    assert utils.get_shift_len(start, end) == 1
    end += timedelta(minutes=12)
    assert utils.get_shift_len(start, end) == 1.2


@pytest.mark.parametrize('date, prev_day, night_times', NIGHT_TIMES)
def test_get_night_times(date, prev_day, night_times):
    assert utils.get_night_times(date, prev_day) == night_times


@pytest.mark.parametrize('start, end, boolean', NIGHT_SHIFTS)
def test_is_night_shift(wage, start, end, boolean):
    assert utils.is_night_shift(start, end, wage) == boolean


# start = datetime(2020, 1, 4, 15)
# end = datetime(2020, 1, 5, 1)
# # end = datetime(2020, 1, 4, 19)

# for i in range(1, 8):
#     a = SalarySettings()
#     a.off_day = i
#     print(a.off_day)
#     # holiday_start, holiday_end = get_relevant_holiday_times(start, end, i, None)
#     #print(holiday_start)
#     print(utils.get_hours_during_holiday(start, end, a))# holiday_start, holiday_end))



# REGULAR_SHIFT = {'start': datetime(2021, 1, 14, 9),
#                 'end': datetime(2021, 1, 14, 19)}
# NIGHT_SHIFT = {'start': datetime(2021, 1, 14, 19),
#                 'end': datetime(2021, 1, 15, 5)}
# OFF_SHIFT = {'start': datetime(2021, 1, 16, 9),
#                 'end': datetime(2021, 1, 16, 19)}
# OFF_NIGHT_SHIFT = {'start': datetime(2021, 1, 16, 4),
#                 'end': datetime(2021, 1, 16, 14)}
# LONG_SHIFT = {'start': datetime(2021, 1, 14, 9),
#                 'end': datetime(2021, 1, 14, 23)}

# SHIFTS = (REGULAR_SHIFT, NIGHT_SHIFT, OFF_SHIFT, OFF_NIGHT_SHIFT, LONG_SHIFT)
# for shift in SHIFTS:
#     print(utils.is_night_shift(**shift, wage=wage))
#     print(utils.adjust_overtime(wage=wage, **shift))
#     print(utils.calc_shift_salary(wage=wage, **shift))



# # DAY_1 = {'start': datetime(2021, 1, 10, 9),
# #          'end': datetime(2021, 1, 10, 19)}
# # DAY_2 = {'start': datetime(2021, 1, 11, 9),
# #          'end': datetime(2021, 1, 11, 17)}
# # DAY_3 = {'start': datetime(2021, 1, 12, 9),
# #          'end': datetime(2021, 1, 12, 17)}
# # DAY_4 = {'start': datetime(2021, 1, 13, 9),
# #          'end': datetime(2021, 1, 13, 18)}
# # DAY_5 = {'start': datetime(2021, 1, 14, 9),
# #          'end': datetime(2021, 1, 14, 17)}

# # DAYS = (DAY_1, DAY_2, DAY_3, DAY_4, DAY_5)

# # print(sum(get_shift_len(**day) for day in DAYS))


# print(utils.calc_weekly_overtime(utils.get_event_by_category(), wage))

# a = utils.calc_salary(2021, 1, wage)
# for key, value in a.items():
#     if key == 'month_weekly_overtime':
#         for week in value:
#             for sub_key, sub_value in week.items():
#                 print(f"{sub_key}: {sub_value}")
#     else:
#         print(f"{key}: {value}")