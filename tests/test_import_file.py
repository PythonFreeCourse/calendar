import datetime

import pytest

from app.internal.import_file import (
    before_import_checking, check_date_in_range, check_file_extension,
    check_file_size, check_validity_of_txt, import_ics_file, import_txt_file,
    is_file_exist, user_click_import)


file_size_tests = [
    # File size above the constraint we set in the global variable (5 MB)
    (r"tests/files_for_import_file_tests/sample_above_5mb.txt", False),
    # File size below the constraint we set in the global variable (5 MB)
    (r"tests/files_for_import_file_tests/sample_below_1mb.txt", True),
    # File size below the constraint we set to the function
    (r"tests/files_for_import_file_tests/sample_above_5mb.txt", 10, True),
    # File size above the constraint we set to the function
    (r"tests/files_for_import_file_tests/sample_above_5mb.txt", 2, False)
]

file_exist_tests = [
    # File exist
    (r"tests/files_for_import_file_tests/sample_below_1mb.txt", True),
    # File not exist
    (r"tests/files_for_import_file_tests/not_exist.txt", False)
]

file_extension_tests = [
    (r"tests/files_for_import_file_tests/sample_below_1mb.txt", True),
    (r"tests/files_for_import_file_tests/sample_below_1mb.csv", True),
    (r"tests/files_for_import_file_tests/sample.ics", True),
    (r"tests/files_for_import_file_tests/sample.blabla", False),
    (r"tests/files_for_import_file_tests/sample.csv.blabla", False)
]

date_in_range_tests = [
    ("01-31-2022", True),
    ("01-32-2022", False),
    ("20-02-2022", False),
    ("1-20-2011", True),
    # date above the constraint we set (20 years after today date)
    ("01-01-2050", False),
    # date below the constraint we set (20 years before today date)
    ("01-01-2000", False),
    # date in the range we set in the function
    ("01-01-2019", 5, True),
    # date below the range we set in the function
    ("01-01-2017", 2, False)
]

check_validity_of_text_tests = [
    (r"Head1, Content1, 05-21-2019", True),
    (r"Head1Content1, 05-21-2019", False),
    # title can't be empty
    (r"  , Content1, 05-21-2019", False),
    # content may be empty
    (r"Head1, , 05-21-2019", True),
    # date can't be empty
    (r"Head1, Content1, ", False),
    # row cant have multiple events
    (r"Head1, Content1, 05-21-2019, Head2, Content2, 05-21-2019", False)
]

import_txt_file_tests = [
    # txt file
    (r"tests/files_for_import_file_tests/sample_calendar_data_to_import_1.txt",
        [
            {'Head': 'Head1', 'Content': 'Content1',
             'Date': datetime.datetime(2019, 5, 21, 0, 0)},
            {'Head': 'Head2', 'Content': 'Content2',
             'Date': datetime.datetime(2010, 1, 11, 0, 0)},
            {'Head': 'Head3', 'Content': 'Content3',
             'Date': datetime.datetime(2022, 2, 2, 0, 0)}
        ]),
    # csv file
    (r"tests/files_for_import_file_tests/sample_calendar_data_to_import_1.csv",
        [
            {'Head': 'Head1', 'Content': 'Content1',
             'Date': datetime.datetime(2019, 5, 21, 0, 0)},
            {'Head': 'Head2', 'Content': 'Content2',
             'Date': datetime.datetime(2010, 1, 11, 0, 0)},
            {'Head': 'Head3', 'Content': 'Content3',
             'Date': datetime.datetime(2022, 2, 2, 0, 0)}
        ])
]

import_ics_tests = [
    # ics file
    (r"tests/files_for_import_file_tests/sample.ics",
        [
            {'Head': 'HeadA', 'Content': 'Content1',
             'Date': datetime.datetime(2019, 8, 2, 10, 34)},
            {'Head': 'HeadB', 'Content': 'Content2',
             'Date': datetime.datetime(2019, 8, 2, 20, 0)}
        ]),
    # ics file
    (r"tests/files_for_import_file_tests/sample2.ics", [])
]

before_import_checking_tests = [
    (r"tests/files_for_import_file_tests/sample_calendar_data_to_import_1.txt",
     True),
    (r"tests/files_for_import_file_tests/sample_above_5mb.txt", False),
    (r"tests/files_for_import_file_tests/sample.blabla", False),
    (r"tests/files_for_import_file_tests/sample2.blabla", False)
]


user_click_import_tests = [
    (r"tests/files_for_import_file_tests/sample_calendar_data_to_import_1.txt",
     1, "Import success"),
    (r"tests/files_for_import_file_tests/sample.ics", 1,
     "Import success"),
    (r"tests/files_for_import_file_tests/sample_above_5mb.txt", 1,
     "Import failed"),
    (r"tests/files_for_import_file_tests/sample.blabla", 1,
     "Import failed"),
    (r"tests/files_for_import_file_tests/sample_same_date_many_times.txt", 1,
     "Import failed")
]


@pytest.mark.parametrize("file", file_size_tests)
def test_check_file_size(file):
    if len(file) == 2:
        assert check_file_size(file[0]) == file[1]
    else:
        assert check_file_size(file[0], file[1]) == file[2]


@pytest.mark.parametrize("file", file_exist_tests)
def test_is_file_exist(file):
    assert is_file_exist(file[0]) == file[1]


@pytest.mark.parametrize("file", file_extension_tests)
def test_check_file_extension(file):
    if len(file) == 2:
        assert check_file_extension(file[0]) == file[1]
    else:
        assert check_file_extension(file[0], file[1]) == file[2]


@pytest.mark.parametrize("date_n_stat", date_in_range_tests)
def test_check_date_in_range(date_n_stat):
    if len(date_n_stat) == 2:
        assert check_date_in_range(date_n_stat[0]) == date_n_stat[1]
    else:
        assert check_date_in_range(date_n_stat[0],
                                   date_n_stat[1]) == date_n_stat[2]


@pytest.mark.parametrize("row", check_validity_of_text_tests)
def test_check_validity_of_text(row):
    assert check_validity_of_txt(row[0]) == row[1]


@pytest.mark.parametrize("file1", import_txt_file_tests)
def test_import_txt_file(file1):
    assert import_txt_file(file1[0]) == file1[1]


@pytest.mark.parametrize("file1", import_ics_tests)
def test_import_ics_file(file1):
    assert import_ics_file(file1[0]) == file1[1]


@pytest.mark.parametrize("file1", before_import_checking_tests)
def test_before_import_checking(file1):
    assert before_import_checking(file1[0]) == file1[1]


@pytest.mark.parametrize("file1", user_click_import_tests)
def test_user_click_import(file1, test_session):
    assert user_click_import(file1[0], file1[1], test_session) == file1[2]
