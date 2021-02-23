from datetime import datetime

import pytest

from app.internal import import_file

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
    {
        'Head': 'Head1',
        'Content': 'Content1',
        'S_Date': datetime(2019, 5, 21),
        'E_Date': datetime(2019, 5, 21),
        'Location': "",
    },
    {
        'Head': 'Head2',
        'Content': 'Content2',
        'S_Date': datetime(2010, 1, 11),
        'E_Date': datetime(2010, 1, 11),
        'Location': "",
    },
    {
        'Head': 'Head3',
        'Content': 'Content3',
        'S_Date': datetime(2022, 2, 2),
        'E_Date': datetime(2022, 2, 2),
        'Location': "",
    },
]

FILE_SIZE_TESTS = [
    # File size above the constraint we set in the global variable (5 MB)
    (FILE_TXT_ABOVE_5MB, None, False),
    # File size below the constraint we set in the global variable (5 MB)
    (FILE_TXT_BELOW_1MB, None, True),
    # File size below the constraint we set to the function
    (FILE_TXT_ABOVE_5MB, 10, True),
    # File size above the constraint we set to the function
    (FILE_TXT_ABOVE_5MB, 2, False),
]

FILE_EXISTS_TESTS = [
    # File exist
    (FILE_TXT_BELOW_1MB, True),
    # File not exist
    (FILE_NOT_EXIST, False),
]

STRING_TO_DATE_TESTS = [
    ("02-28-2022 13:05", datetime(2022, 2, 28, 13, 5)),
    ("02-28-2022", datetime(2022, 2, 28)),
    ("01-32-2022 20:30", None),  # Invalid Date
]

START_DAY_END_DAY_TESTS = [
    (datetime(1991, 12, 1, 10), datetime(1991, 12, 1, 11), True),
    (datetime(1991, 12, 1, 11), datetime(1991, 12, 1, 10), False),
]

VALID_DATES_TESTS = [
    ("02-26-2022", "02-27-2022", True),
    ("02-27-2022", "02-26-2022", False),
    ("not a date", "02-28-2022", False),
]

FILE_EXTENSION_TESTS = [
    (FILE_TXT_BELOW_1MB, None, True),
    (FILE_CSV_BELOW_1MB, None, True),
    (FILE_ICS, None, True),
    (NOT_EXIST_BLABLA_EXTENSION, ".blabla", True),
    (NOT_EXIST_BLABLA_EXTENSION, None, False),
    (r"tests/files_for_import_file_tests/sample.csv.blabla", None, False),
]

DATE_IN_RANGE_TESTS = [
    (datetime(2022, 1, 31), None, True),
    (datetime(2022, 1, 31, 10, 30), None, True),
    (datetime(2011, 1, 20), None, True),
    # date above the constraint we set (20 years after today date)
    (datetime(2050, 1, 1), None, False),
    # date below the constraint we set (20 years before today date)
    (datetime(2000, 1, 1), None, False),
    # date in the range we set in the function
    (datetime(2019, 1, 1), 5, True),
    # date below the range we set in the function
    (datetime(2018, 1, 1), 2, False),
]

EVENT_DURATION_TESTS = [
    (datetime(1991, 12, 1), datetime(1991, 12, 2), None, True),
    (datetime(1991, 12, 1, 10, 30), datetime(1991, 12, 3, 10, 29), None, True),
    (
        datetime(1991, 12, 1, 10, 30), datetime(1991, 12, 3, 10, 30), None,
        False,
    ),
    (datetime(1991, 12, 1, 10, 30), datetime(1991, 12, 5, 10, 30), 5, True),
]

TEXT_VALID_TESTS = [
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
    (r"Head1, Content1, 05-21-2019, 06-21-2019, New York-1", True),
]

IMPORT_TXT_FILE_TESTS = [
    # txt file
    (FILE_TXT_SAMPLE, IMPORT_TXT_FILE_RESULT_DATA),
    # csv file
    (FILE_CSV_SAMPLE, IMPORT_TXT_FILE_RESULT_DATA),
    # Invalid text structure
    (FILE_TXT_INVALID, []),
    # Invalid date range
    (FILE_RNG_INVALID, []),
]

IMPORT_ICS_FILE_TESTS = [
    # ics file
    (FILE_ICS,
     [
         {
             'Head': 'HeadA',
             'Content': 'Content1',
             'S_Date': datetime(2019, 8, 2, 10, 34),
             'E_Date': datetime(2019, 8, 2, 11, 4),
             'Location': 'Tel-Aviv',
         },
         {
             'Head': 'HeadB',
             'Content': 'Content2',
             'S_Date': datetime(2019, 8, 2, 20),
             'E_Date': datetime(2019, 8, 2, 20, 30),
             'Location': 'Tel-Aviv',
         }
     ]),
    # ics invalid file
    (FILE_ICS_INVALID_DATA, []),
    # ics invalid file
    (FILE_ICS_INVALID_DATA2, []),
]

FILE_VALID_TO_SAVE_TESTS = [
    (FILE_TXT_SAMPLE, True),
    (FILE_TXT_DATE_VER, True),
    (FILE_TXT_LOCATION, True),
    (FILE_TXT_ABOVE_5MB, False),
    (NOT_EXIST_BLABLA_EXTENSION, False),
    (FILE_BLABLA_EXTENSION, False),
]

IMPORT_EVENTS_TESTS = [
    (FILE_TXT_SAMPLE, 1, True),
    (FILE_TXT_DATE_VER, 1, True),
    (FILE_TXT_LOCATION, 1, True),
    (FILE_ICS, 1, True),
    (FILE_TXT_ABOVE_5MB, 1, False),
    (NOT_EXIST_BLABLA_EXTENSION, 1, False),
    (FILE_TXT_BELOW_1MB, 1, False),
    (FILE_TXT_MIX_DATE, 1, False),
]


@pytest.mark.parametrize("test_file, max_size, expected", FILE_SIZE_TESTS)
def test_is_file_size_valid(test_file, max_size, expected):
    if max_size is None:
        assert import_file._is_file_size_valid(test_file) == expected
    else:
        assert import_file._is_file_size_valid(test_file, max_size) == expected


@pytest.mark.parametrize("test_file, expected", FILE_EXISTS_TESTS)
def test_is_file_exists(test_file, expected):
    assert import_file._is_file_exists(test_file) == expected


@pytest.mark.parametrize("date, expected", STRING_TO_DATE_TESTS)
def test_convert_string_to_date(date, expected):
    assert import_file._convert_string_to_date(date) == expected


@pytest.mark.parametrize("start, end, expected", START_DAY_END_DAY_TESTS)
def test_is_start_day_before_end_date(start, end, expected):
    assert import_file._is_start_date_before_end_date(start, end) == expected


@pytest.mark.parametrize("start, end, is_valid", VALID_DATES_TESTS)
def test_is_event_dates_valid(start, end, is_valid):
    assert import_file._is_event_dates_valid(start, end) == is_valid


@pytest.mark.parametrize("test_file, extension, expected",
                         FILE_EXTENSION_TESTS)
def test_is_file_extension_valid(test_file, extension, expected):
    if extension is None:
        assert import_file._is_file_extension_valid(test_file) == expected
    else:
        assert import_file._is_file_extension_valid(test_file,
                                                    extension) == expected


@pytest.mark.parametrize("date, valid_dates, expected", DATE_IN_RANGE_TESTS)
def test_is_date_in_range(date, valid_dates, expected):
    if valid_dates is None:
        assert import_file._is_date_in_range(date) == expected
    else:
        assert import_file._is_date_in_range(date, valid_dates) == expected


@pytest.mark.parametrize("text, expected", TEXT_VALID_TESTS)
def test_is_event_text_valid(text, expected):
    assert import_file._is_event_text_valid(text) == expected


@pytest.mark.parametrize("test_file, expected", IMPORT_TXT_FILE_TESTS)
def test_get_data_from_txt_file(test_file, expected):
    assert import_file._get_data_from_txt_file(test_file) == expected


@pytest.mark.parametrize("test_file, expected", IMPORT_ICS_FILE_TESTS)
def test_get_data_from_ics_file(test_file, expected):
    assert import_file._get_data_from_ics_file(test_file) == expected


@pytest.mark.parametrize(
    "start, end, max_duration, expected", EVENT_DURATION_TESTS)
def test_is_event_valid_duration(start, end, max_duration, expected):
    if max_duration is None:
        assert import_file._is_event_duration_valid(start, end) == expected
    else:
        result = import_file._is_event_duration_valid(start, end, max_duration)
        assert result == expected


@pytest.mark.parametrize("test_file, expected", FILE_VALID_TO_SAVE_TESTS)
def test_is_file_valid_to_import(test_file, expected):
    assert import_file._is_file_valid_to_import(test_file) == expected


@pytest.mark.parametrize("test_file, user_id, expected", IMPORT_EVENTS_TESTS)
def test_import_events(test_file, user_id, expected, session):
    assert import_file.import_events(test_file, user_id, session) == expected
