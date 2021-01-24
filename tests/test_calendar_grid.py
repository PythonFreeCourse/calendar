import datetime
from http import HTTPStatus

import app.routers.calendar_grid as cg

DATE = datetime.date(1988, 5, 3)
DAY = cg.Day(datetime.date(1988, 5, 3))
WEEKEND = cg.DayWeekend(datetime.date(2021, 1, 23))
N_DAYS = 3
N_DAYS_BEFORE = datetime.date(1988, 4, 30)
NEXT_N_DAYS = [
    cg.Day(datetime.date(1988, 5, 4)),
    cg.Day(datetime.date(1988, 5, 5)),
    cg.Day(datetime.date(1988, 5, 6))
]
DAY_TYPES = [cg.Day, cg.DayWeekend, cg.Today, cg.FirstDayMonth]
WEEK_DAYS = cg.Week.WEEK_DAYS


class TestCalendarGrid:
    @staticmethod
    def test_get_calendar(client):
        response = client.get("/calendar")
        assert response.status_code == HTTPStatus.OK
        assert b"SUNDAY" in response.content

    @staticmethod
    def test_get_calendar_extends(client):
        response = client.get(f"/calendar/{DAY.display()}")
        assert response.status_code == HTTPStatus.OK
        assert b"08" in response.content

    @staticmethod
    def test_create_day():
        dates_to_check = {
            'normal_day': datetime.date(2021, 1, 20),
            'weekend': datetime.date(2021, 1, 23),
            'today': datetime.date.today(),
            'first_month': datetime.date(2021, 1, 1)
        }

        for i, value in enumerate(dates_to_check.values()):
            assert isinstance(cg.create_day(value), DAY_TYPES[i])

    @staticmethod
    def test_get_next_date():
        next_day_generator = cg.get_next_date(DATE)
        next_day = next(next_day_generator, None)
        next_day_check = cg.Day(DATE + datetime.timedelta(days=1))
        assert next_day
        assert isinstance(next_day, cg.Day)
        assert next_day.date == next_day_check.date

    @staticmethod
    def test_get_date_before_n_days():
        assert cg.get_date_before_n_days(DATE, N_DAYS) == N_DAYS_BEFORE

    @staticmethod
    def test_get_first_day_month_block(Calendar):
        assert (
            cg.get_first_day_month_block(DATE)
            == next(Calendar.itermonthdates(DATE.year, DATE.month))
        )

    @staticmethod
    def test_get_n_days():
        next_n_dates = cg.get_n_days(DATE, N_DAYS)
        for i in range(N_DAYS):
            assert next(next_n_dates).date == NEXT_N_DAYS[i].date

    @staticmethod
    def test_split_list_to_lists():
        s_length = 7
        t_length = 20
        list_before_split = list(range(t_length))
        list_after_split = [
            list_before_split[i: i + s_length]
            for i in range(0, len(list_before_split), s_length)
        ]
        assert (
            cg.split_list_to_lists(list_before_split, s_length)
            == list_after_split
        )

    @staticmethod
    def test_get_month_block(Calendar):
        month_days = cg.split_list_to_lists(
            list(Calendar.itermonthdates(1988, 5)), WEEK_DAYS)
        get_block = cg.get_month_block(
            cg.Day(DATE), n=len(month_days) * WEEK_DAYS)
        print(get_block[0][0].date)
        print(get_block[-1][-1].date)
        for i in range(len(month_days)):
            for j in range(7):
                assert get_block[i][j].date == month_days[i][j]

    @staticmethod
    def test_is_weekend():
        assert not cg.Day.is_weekend(DATE)
        assert cg.Day.is_weekend(WEEKEND.date)

    @staticmethod
    def test_display_day():
        assert DAY.display() == '03 MAY 88'

    @staticmethod
    def test_display_str():
        assert str(DAY) == '03'
