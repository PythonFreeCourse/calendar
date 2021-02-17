import datetime

from app.routers import calendar_grid

DATE = datetime.date(1988, 5, 3)
DAY = calendar_grid.Day(datetime.date(1988, 5, 3))
WEEKEND = calendar_grid.DayWeekend(datetime.date(2021, 1, 23))
N_DAYS = 3
N_DAYS_BEFORE = datetime.date(1988, 4, 30)
NEXT_N_DAYS = [
    calendar_grid.Day(datetime.date(1988, 5, 4)),
    calendar_grid.Day(datetime.date(1988, 5, 5)),
    calendar_grid.Day(datetime.date(1988, 5, 6))
]
DAY_TYPES = [calendar_grid.Day, calendar_grid.DayWeekend,
             calendar_grid.Today, calendar_grid.FirstDayMonth]
WEEK_DAYS = calendar_grid.Week.WEEK_DAYS


class TestCalendarGrid:
    @staticmethod
    def test_get_calendar(client):
        response = client.get("/calendar/month")
        assert response.ok
        assert b"SUNDAY" in response.content

    @staticmethod
    def test_get_calendar_extends(client):
        days = 42
        response = client.get(
            f"/calendar/month/add/{DAY.set_id()}?days={days}"
        )
        assert response.ok
        assert b"08-May" in response.content

    @staticmethod
    def test_create_day():
        dates_to_check = {
            'normal_day': datetime.date(2021, 1, 20),
            'weekend': datetime.date(2021, 1, 23),
            'today': datetime.date.today(),
            'first_month': datetime.date(2021, 1, 1)
        }

        for i, value in enumerate(dates_to_check.values()):
            assert isinstance(calendar_grid.create_day(value), DAY_TYPES[i])

    @staticmethod
    def test_get_next_date():
        next_day_generator = calendar_grid.get_next_date(DATE)
        next_day = next(next_day_generator, None)
        next_day_check = calendar_grid.Day(DATE + datetime.timedelta(days=1))
        assert next_day
        assert isinstance(next_day, calendar_grid.Day)
        assert next_day.date == next_day_check.date

    @staticmethod
    def test_get_date_before_n_days():
        assert calendar_grid.get_date_before_n_days\
                   (DATE, N_DAYS) == N_DAYS_BEFORE

    @staticmethod
    def test_get_first_day_month_block(Calendar):
        assert (
                calendar_grid.get_first_day_month_block(DATE)
                == next(Calendar.itermonthdates(DATE.year, DATE.month))
        )

    @staticmethod
    def test_get_n_days():
        next_n_dates = calendar_grid.get_n_days(DATE, N_DAYS)
        for i in range(N_DAYS):
            assert next(next_n_dates).date == NEXT_N_DAYS[i].date

    @staticmethod
    def test_create_weeks():
        week = calendar_grid.create_weeks(
            NEXT_N_DAYS, calendar_grid.Week.WEEK_DAYS)
        assert week
        assert isinstance(week[0], calendar_grid.Week)
        assert isinstance(week[0].days[0], calendar_grid.Day)
        assert len(week) == 1 and len(week[0].days) == 3

    @staticmethod
    def test_get_month_block(Calendar):
        month_weeks = calendar_grid.create_weeks(
            Calendar.itermonthdates(1988, 5), WEEK_DAYS)
        get_block = calendar_grid.get_month_block(
            calendar_grid.Day(DATE), n=len(month_weeks))

        for i in range(len(month_weeks)):
            for j in range(calendar_grid.Week.WEEK_DAYS):
                assert get_block[i].days[j].date == month_weeks[i].days[j]

    @staticmethod
    def test_get_user_local_time():
        time_string = "%b%w%Y"
        server_time = calendar_grid.Day.get_user_local_time()
        server_time_check = datetime.datetime.today()
        assert server_time
        assert server_time.strftime(
            time_string) == server_time_check.strftime(time_string)

    @staticmethod
    def test_is_weekend():
        assert not calendar_grid.Day.is_weekend(DATE)
        assert calendar_grid.Day.is_weekend(WEEKEND.date)

    @staticmethod
    def test_display_day():
        assert DAY.display() == '03 MAY 88'

    @staticmethod
    def test_set_id():
        assert DAY.set_id() == '03-May-1988'

    @staticmethod
    def test_display_str():
        assert str(DAY) == '03'

    @staticmethod
    def test_create_week_object():
        assert calendar_grid.Week(NEXT_N_DAYS)
