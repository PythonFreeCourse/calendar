import datetime

import pytest

from app.internal.import_file import (
    change_string_to_date, import_ics_file, import_txt_file, is_date_in_range,
    is_event_text_valid, is_event_valid_duration, is_file_exist,
    is_file_extension_valid, is_file_size_valid, is_file_valid_to_import,
    is_start_day_before_end_date, user_click_import)


FILE_TXT_SAMPLE = r"tests/files_for_import_file_tests/sample_calendar_data.txt"
FILE_TXT_INVALID = r"tests/files_for_import_file_tests/sample_data_invalid.txt"
FILE_RNG_INVALID = r"tests/files_for_import_file_tests/sample_rng_invalid.txt"
FILE_CSV_SAMPLE = r"tests/files_for_import_file_tests/sample_calendar_data.csv"
FILE_TXT_ABOVE_5MB = r"tests/files_for_import_file_tests/sample_above_5mb.txt"
FILE_TXT_BELOW_1MB = r"tests/files_for_import_file_tests/sample_below_1mb.txt"
FILE_CSV_BELOW_1MB = r"tests/files_for_import_file_tests/sample_below_1mb.csv"
FILE_NOT_EXIST = r"tests/files_for_import_file_tests/not_exist.txt"
FILE_ICS = r"tests/files_for_import_file_tests/sample.ics"
FILE_ICS_INVALID_DATA = r"tests/files_for_import_file_tests/sample2.ics"
FILE_ICS_INVALID_DATA2 = r"tests/files_for_import_file_tests/sample3.ics"
NOT_EXIST_BLABLA_EXTENSION = r"tests/files_for_import_file_tests/sample.blabla"
FILE_BLABLA_EXTENSION = r"tests/files_for_import_file_tests/sample2.blabla"
FILE_TXT_DATE_VER = r"tests/files_for_import_file_tests/sample_date2_ver.txt"
FILE_TXT_LOCATION = r"tests/files_for_import_file_tests/‏‏sample_loc_ver.txt"
FILE_TXT_MIX_DATE = r"tests/files_for_import_file_tests/‏‏sample_date_mix.txt"


IMPORT_TXT_FILE_RESULT_DATA = [
    {'Head': 'Head1', 'Content': 'Content1',
     'S_Date': datetime.datetime(2019, 5, 21, 0, 0),
     'E_Date': datetime.datetime(2019, 5, 21, 0, 0),
     'Location': None},
    {'Head': 'Head2', 'Content': 'Content2',
     'S_Date': datetime.datetime(2010, 1, 11, 0, 0),
     'E_Date': datetime.datetime(2010, 1, 11, 0, 0),
     'Location': None},
    {'Head': 'Head3', 'Content': 'Content3',
     'S_Date': datetime.datetime(2022, 2, 2, 0, 0),
     'E_Date': datetime.datetime(2022, 2, 2, 0, 0),
     'Location': None},
]


file_size_tests = [
    # File size above the constraint we set in the global variable (5 MB)
    (FILE_TXT_ABOVE_5MB, None, False),
    # File size below the constraint we set in the global variable (5 MB)
    (FILE_TXT_BELOW_1MB, None, True),
    # File size below the constraint we set to the function
    (FILE_TXT_ABOVE_5MB, 10, True),
    # File size above the constraint we set to the function
    (FILE_TXT_ABOVE_5MB, 2, False)
]

file_exist_tests = [
    # File exist
    (FILE_TXT_BELOW_1MB, True),
    # File not exist
    (FILE_NOT_EXIST, False)
]

change_string_to_date_tests = [
    ("02-28-2022 13:05", datetime.datetime(2022, 2, 28, 13, 5)),
    ("02-28-2022", datetime.datetime(2022, 2, 28)),
    ("01-32-2022 20:30", False),  # Invalid Date
]

start_day_before_end_date_tests = [
    (datetime.datetime(1991, 12, 1, 10),
     datetime.datetime(1991, 12, 1, 11), True),
    (datetime.datetime(1991, 12, 1, 11),
     datetime.datetime(1991, 12, 1, 10), False)
]

file_extension_tests = [
    (FILE_TXT_BELOW_1MB, None, True),
    (FILE_CSV_BELOW_1MB, None, True),
    (FILE_ICS, None, True),
    (NOT_EXIST_BLABLA_EXTENSION, ".blabla", True),
    (NOT_EXIST_BLABLA_EXTENSION, None, False),
    (r"tests/files_for_import_file_tests/sample.csv.blabla", None, False)
]

date_in_range_tests = [
    ("01-31-2022", None, True),
    ("01-32-2022", None, False),
    ("01-31-2022 10:30", None, True),
    ("01-32-2022 10:30", None, False),
    ("20-02-2022", None, False),
    ("1-20-2011", None, True),
    # date above the constraint we set (20 years after today date)
    ("01-01-2050", None, False),
    # date below the constraint we set (20 years before today date)
    ("01-01-2000", None, False),
    # date in the range we set in the function
    ("01-01-2019", 5, True),
    # date below the range we set in the function
    ("01-01-2017", 2, False)
]

is_event_valid_duration_tests = [
    (datetime.datetime(1991, 12, 1),
     datetime.datetime(1991, 12, 2), None, True),
    (datetime.datetime(1991, 12, 1, 10, 30),
     datetime.datetime(1991, 12, 3, 10, 29), None, True),
    (datetime.datetime(1991, 12, 1, 10, 30),
     datetime.datetime(1991, 12, 3, 10, 30), None, False),
    (datetime.datetime(1991, 12, 1, 10, 30),
     datetime.datetime(1991, 12, 5, 10, 30), 5, True)
]


check_validity_of_text_tests = [
    (r"Head1, Content1, 05-21-2019, 05-21-2019", True),
    (r"Head1, Content1, 05-21-2019 10:30, 05-21-2019 11:30", True),
    (r"Head1, Content1, 05-21-2019 10:30, 05-21-2019 11:30, Tel-Aviv", True),
    (r"Head1Content1, 05-21-2019, 05-21-2019", False),
    # title can't be empty
    (r"  , Content1, 05-21-2019, 05-21-2019", False),
    # content may be empty
    (r"Head1, , 05-21-2019, 05-21-2019", True),
    # start_date can't be empty
    (r"Head1, Content1, , 05-21-2019", False),
    # end_date can't be empty
    (r"Head1, Content1, 05-21-2019, ", False),
    # row cant have multiple events
    (r"""Head1, Content1, 05-21-2019, 05-21-2019,
     Head2, Content2, 05-21-2019, 05-21-2019""", False),
    # dates cant be from a different formats
    (r"Head1, Content1, 05-21-2019 10:30, 06-21-2019, Tel-Aviv", False),
    # location may be empty
    (r"Head1, Content1, 05-21-2019 10:30, 06-21-2019 11:30, ", True),
    # location may have space and dash
    (r"Head1, Content1, 05-21-2019, 06-21-2019, New York-1", True)
]

import_txt_file_tests = [
    # txt file
    (FILE_TXT_SAMPLE, IMPORT_TXT_FILE_RESULT_DATA),
    # csv file
    (FILE_CSV_SAMPLE, IMPORT_TXT_FILE_RESULT_DATA),
    # Invalid text structure
    (FILE_TXT_INVALID, []),
    # Invalid date range
    (FILE_RNG_INVALID, [])
]

import_ics_tests = [
    # ics file
    (FILE_ICS,
        [
            {'Head': 'HeadA', 'Content': 'Content1',
             'S_Date': datetime.datetime(2019, 8, 2, 10, 34),
             'E_Date': datetime.datetime(2019, 8, 2, 11, 4),
             'Location': 'Tel-Aviv'},
            {'Head': 'HeadB', 'Content': 'Content2',
             'S_Date': datetime.datetime(2019, 8, 2, 20, 0),
             'E_Date': datetime.datetime(2019, 8, 2, 20, 30),
             'Location': 'Tel-Aviv'
             }
        ]),
    # ics invalid file
    (FILE_ICS_INVALID_DATA, []),
    # ics invalid file
    (FILE_ICS_INVALID_DATA2, [])
]

is_file_valid_to_import_tests = [
    (FILE_TXT_SAMPLE, True),
    (FILE_TXT_DATE_VER, True),
    (FILE_TXT_LOCATION, True),
    (FILE_TXT_ABOVE_5MB, False),
    (NOT_EXIST_BLABLA_EXTENSION, False),
    (FILE_BLABLA_EXTENSION, False)
]

save_calendar_content_txt_tests = [
    ("Head, Content, 05-21-2019 10:30, 05-21-2019 11:30, Tel-Aviv", [], True),
    ("Head, Content, 05-21-2019 10:30, 05-21-2019, Tel-Aviv", [], False),
]

user_click_import_tests = [
    (FILE_TXT_SAMPLE, 1, True),
    (FILE_TXT_DATE_VER, 1, True),
    (FILE_TXT_LOCATION, 1, True),
    (FILE_ICS, 1, True),
    (FILE_TXT_ABOVE_5MB, 1, False),
    (NOT_EXIST_BLABLA_EXTENSION, 1, False),
    (FILE_TXT_BELOW_1MB, 1, False),
    (FILE_TXT_MIX_DATE, 1, False)
]


@pytest.mark.parametrize("file1, max_size, result", file_size_tests)
def test_is_file_size_valid(file1, max_size, result):
    if max_size is None:
        assert is_file_size_valid(file1) == result
    else:
        assert is_file_size_valid(file1, max_size) == result


@pytest.mark.parametrize("file1, result", file_exist_tests)
def test_is_file_exist(file1, result):
    assert is_file_exist(file1) == result


@pytest.mark.parametrize("str1, result", change_string_to_date_tests)
def test_change_string_to_date(str1, result):
    assert change_string_to_date(str1) == result


@pytest.mark.parametrize("start, end, result", start_day_before_end_date_tests)
def test_is_start_day_before_end_date(start, end, result):
    assert is_start_day_before_end_date(start, end) == result


@pytest.mark.parametrize("file1, extension, result", file_extension_tests)
def test_is_file_extension_valid(file1, extension, result):
    if extension is None:
        assert is_file_extension_valid(file1) == result
    else:
        assert is_file_extension_valid(file1, extension) == result


@pytest.mark.parametrize("date, valid_dates, result", date_in_range_tests)
def test_is_date_in_range(date, valid_dates, result):
    if valid_dates is None:
        assert is_date_in_range(date) == result
    else:
        assert is_date_in_range(date, valid_dates) == result


@pytest.mark.parametrize("row, result", check_validity_of_text_tests)
def test_check_validity_of_text(row, result):
    assert is_event_text_valid(row) == result


@pytest.mark.parametrize("file1, result", import_txt_file_tests)
def test_import_txt_file(file1, result):
    assert import_txt_file(file1) == result


@pytest.mark.parametrize("file1, result", import_ics_tests)
def test_import_ics_file(file1, result):
    assert import_ics_file(file1) == result


@pytest.mark.parametrize("start, end, max_duration, result",
                         is_event_valid_duration_tests)
def test_is_event_valid_duration(start, end, max_duration, result):
    if max_duration is None:
        assert is_event_valid_duration(start, end) == result
    else:
        assert is_event_valid_duration(start, end, max_duration) == result


@pytest.mark.parametrize("file1, result", is_file_valid_to_import_tests)
def test_is_file_valid_to_import(file1, result):
    assert is_file_valid_to_import(file1) == result


@pytest.mark.parametrize("event, cal_content, result",
                         save_calendar_content_txt_tests)
def save_calendar_content_txt(event, cal_content, result, session):
    assert save_calendar_content_txt(event, cal_content, session) == result


@pytest.mark.parametrize("file1, user_id, result", user_click_import_tests)
def test_user_click_import(file1, user_id, result, session):
    assert user_click_import(file1, user_id, session) == result
