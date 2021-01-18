import datetime

import app.routers.calendar_grid as cg

DATE = datetime.date(1988, 5, 3)
N_DAYS = 3
N_DAYS_BEFORE = datetime.date(1988, 4, 30)
NEXT_N_DAYS = [
    datetime.date(1988, 5, 4),
    datetime.date(1988, 5, 5),
    datetime.date(1988, 5, 6)
]


class TestCalendarGrid:
    @staticmethod
    def test_get_date_as_string():
        assert cg.get_date_as_string(DATE) == [
            'Tuesday', 'May', 'May', '1988']

    @staticmethod
    def test_get_next_date():
        next_day = DATE + datetime.timedelta(days=1)
        next_day_generator = cg.get_next_date(DATE)
        assert next(next_day_generator) == next_day

    @staticmethod
    def test_get_date_before_n_days():
        assert cg.get_date_before_n_days(DATE, N_DAYS) == N_DAYS_BEFORE

    @staticmethod
    def test_get_n_days():
        next_n_dates = cg.get_n_days(DATE, N_DAYS)
        for i in range(N_DAYS):
            assert next(next_n_dates) == NEXT_N_DAYS[i]

    @staticmethod
    def test_get_first_day_month_block(Calendar):
        assert (
            cg.get_first_day_month_block(DATE)
            == list(Calendar.itermonthdates(DATE.year, DATE.month))[0]
        )

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
        test = cg.split_list_to_lists(
            list(Calendar.itermonthdates(1988, 5)), 7)
        assert cg.get_month_block(DATE, n=41) == test
