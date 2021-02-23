from datetime import date

import pytest

from app.database.models import InternationalDays
from app.internal import international_days
from app.internal.json_data_loader import load_to_database
from app.internal.utils import create_model, delete_instance

DATE = date(2021, 6, 1)
DAY = "Hamburger day"
ALL_DATES = [(7, 3), (16, 9), (19, 4), (20, 7), (21, 6), (8, 5), (10, 7),
             (14, 1), (15, 4), (26, 12), (3, 2), (27, 1), (4, 5), (28, 10),
             (29, 11), (18, 10), (8, 12), (22, 12), (9, 9), (23, 9), (14, 8),
             (12, 8), (3, 11), (27, 6), (4, 12), (28, 1), (2, 12), (5, 1),
             (29, 4), (16, 7), (17, 6), (18, 5), (21, 8), (22, 7), (23, 6),
             (10, 9), (11, 4), (12, 7), (15, 10), (13, 6), (24, 2), (25, 3),
             (4, 11), (2, 7), (5, 10), (6, 1), (7, 4), (19, 1), (24, 9),
             (25, 4), (26, 3), (27, 10), (30, 5), (16, 11), (19, 6), (17, 10),
             (20, 1), (21, 4), (8, 7), (22, 11), (9, 6), (10, 5), (11, 8),
             (14, 7), (15, 6), (26, 10), (3, 4), (27, 3), (30, 12), (4, 7),
             (28, 4), (5, 6), (29, 9), (16, 2), (17, 3), (20, 8), (18, 8),
             (22, 2), (23, 11), (10, 12), (11, 1), (12, 10), (13, 11), (28, 3),
             (2, 10), (29, 2), (6, 12), (17, 4), (7, 9), (18, 3), (22, 5),
             (11, 6), (12, 1), (13, 4), (24, 4), (1, 6), (25, 1), (2, 5),
             (26, 6), (5, 8), (6, 7), (7, 6), (31, 5), (19, 3), (20, 4),
             (8, 2), (9, 3), (24, 11), (14, 2), (25, 10), (26, 1), (3, 1),
             (27, 12), (30, 11), (19, 8), (17, 8), (20, 3), (21, 2), (8, 9),
             (22, 9), (9, 4), (23, 12), (10, 3), (11, 10), (14, 5), (26, 8),
             (3, 6), (27, 5), (1, 10), (4, 1), (28, 6), (5, 4), (29, 7),
             (16, 4), (6, 11), (17, 1), (20, 10), (18, 6), (21, 11), (23, 5),
             (10, 10), (11, 3), (14, 12), (12, 4), (15, 9), (13, 9), (1, 3),
             (4, 8), (2, 8), (6, 2), (7, 11), (18, 1), (23, 2), (12, 3),
             (13, 2), (24, 6), (1, 4), (25, 7), (2, 3), (26, 4), (27, 9),
             (6, 5), (30, 6), (31, 7), (16, 8), (19, 5), (20, 6), (21, 7),
             (8, 4), (9, 1), (10, 6), (25, 8), (15, 5), (3, 3), (30, 9),
             (4, 4), (28, 9), (31, 12), (29, 12), (19, 10), (8, 11), (9, 10),
             (10, 1), (11, 12), (14, 11), (15, 2), (3, 8), (27, 7), (1, 8),
             (4, 3), (5, 2), (29, 5), (16, 6), (6, 9), (17, 7), (7, 12),
             (18, 4), (21, 9), (22, 6), (23, 7), (10, 8), (11, 5), (12, 6),
             (15, 11), (13, 7), (24, 1), (1, 1), (4, 10), (2, 6), (5, 11),
             (7, 5), (24, 8), (25, 5), (2, 1), (26, 2), (27, 11), (30, 4),
             (28, 12), (7, 2), (31, 1), (16, 10), (19, 7), (17, 11), (21, 5),
             (8, 6), (22, 10), (9, 7), (10, 4), (11, 9), (14, 6), (15, 7),
             (3, 5), (4, 6), (28, 11), (5, 7), (29, 10), (16, 1), (19, 12),
             (17, 12), (18, 11), (9, 8), (23, 8), (14, 9), (12, 9), (15, 12),
             (13, 12), (3, 10), (28, 2), (29, 3), (17, 5), (18, 2), (22, 4),
             (23, 1), (11, 7), (13, 5), (24, 3), (1, 7), (25, 2), (2, 4),
             (5, 9), (6, 6), (30, 3), (7, 7), (8, 1), (24, 10), (25, 11),
             (30, 10), (31, 3), (16, 12), (19, 9), (17, 9), (20, 2), (21, 3),
             (8, 8), (22, 8), (9, 5), (10, 2), (11, 11), (14, 4), (12, 12),
             (25, 12), (15, 1), (26, 11), (3, 7), (27, 2), (1, 11), (28, 5),
             (31, 8), (5, 5), (29, 8), (16, 3), (6, 10), (17, 2), (20, 9),
             (18, 9), (21, 12), (22, 3), (23, 10), (12, 11), (13, 10), (3, 12),
             (1, 12), (2, 11), (29, 1), (7, 8), (23, 3), (12, 2), (13, 3),
             (24, 5), (1, 5), (2, 2), (26, 7), (6, 4), (30, 1), (7, 1),
             (19, 2), (20, 5), (8, 3), (9, 2), (24, 12), (14, 3), (25, 9),
             (30, 8), (28, 8), (19, 11), (20, 12), (18, 12), (21, 1), (8, 10),
             (9, 11), (14, 10), (15, 3), (26, 9), (3, 9), (27, 4), (1, 9),
             (4, 2), (28, 7), (31, 10), (5, 3), (29, 6), (16, 5), (6, 8),
             (20, 11), (18, 7), (21, 10), (22, 1), (9, 12), (23, 4), (10, 11),
             (11, 2), (12, 5), (15, 8), (13, 8), (1, 2), (4, 9), (2, 9),
             (5, 12), (6, 3), (7, 10), (13, 1), (24, 7), (25, 6), (26, 5),
             (27, 8), (30, 7)]



def open_resource(path):
    all_dates = []
    with open(path, 'r') as json_reader:
        days_json = json_reader.read()
        for day in days_json:
            all_dates.append((day["day"], day["month"]))
    return all_dates


@pytest.fixture
def international_day(session):
    inter_day = create_model(
        session, InternationalDays, id=1, day=1, month=6,
        international_day="Hamburger day"
    )
    yield inter_day
    delete_instance(session, inter_day)


@pytest.fixture
def all_international_days(session):
    load_to_database(session)
    all_international_days = list(set(list(session.query(InternationalDays))))
    yield all_international_days
    for day in all_international_days:
        delete_instance(session, day)


def test_input_day_equal_output_day(session, international_day):
    inter_day = international_days.get_international_day_per_day(
        session, DATE).international_day
    assert inter_day == DAY


def test_international_day_per_day_no_international_days(session):
    assert international_days.get_international_day_per_day(session,
                                                            DATE) is None


def test_all_international_days_per_day(session, all_international_days):
    all_days = list(set(list(session.query(InternationalDays))))
    for count, day in enumerate(all_international_days):
        assert day.day, day.month == ALL_DATES[count]
        assert day.international_day == all_days[count]
