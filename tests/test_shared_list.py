from collections import namedtuple

import pytest
from starlette.datastructures import MultiDict

from app.routers.event import (
    _check_item_is_valid,
    _create_shared_list,
    extract_shared_list_from_data,
)

TEST_SHARED_LISTS = [
    {
        "Choco list": [
            {
                "name": "Chocolate",
                "amount": 2,
                "participant": "Elior",
                "notes": "Maltesers are awesome!",
            },
        ],
    },
    {
        "TestList": [
            {"name": "Notebooks", "amount": 2.5, "participant": "Efrat"},
        ],
    },
]

VALID_DATA = MultiDict(
    title="test title",
    start_date="2021-01-28",
    start_time="12:59",
    end_date="2021-01-28",
    end_time="15:01",
    location_type="vc_url",
    location="https://us02web.zoom.us/j/875384596",
    description="content",
    color="red",
    availability="True",
    privacy="public",
    invited="a@a.com,b@b.com",
)

WRONG_DATA = MultiDict(
    title="test title",
    start_date="2021-01-28",
    start_time="12:59",
    end_date="2021-01-28",
    end_time="15:01",
    location_type="vc_url",
    location="https://us02web.zoom.us/j/875384596",
    description="content",
    color="red",
    availability="True",
    privacy="public",
    invited="a@a.com,b@b.com",
)


@pytest.mark.parametrize("test_list", TEST_SHARED_LISTS)
def test_create_shared(test_list, session):
    """Check the shared list build function and
    communication with db is working."""
    shared_list = _create_shared_list(test_list, session)
    assert (
        shared_list.title == list(test_list.keys())[0]
        or shared_list.title == "Shared List"
    )
    assert shared_list.items[0].name == list(test_list.values())[0][0]["name"]


def test_create_shared_list(session):
    """Test shared list with wrong data is not created."""
    assert _create_shared_list(MultiDict(), session) is None


def test_extract_shared_list_from_data_correct(session):
    """Check the shared list extraction function is working."""
    VALID_DATA.setlist("item-name", ["Vanilla", "Strawberries", "Coffee"])
    VALID_DATA.setlist("item-amount", ["3", "2", "1"])
    VALID_DATA.setlist("item-participant", ["Elior", "Efrat", "Yam"])
    assert len(extract_shared_list_from_data(VALID_DATA, session).items) == 3


def test_extract_shared_list_from_data_false_info(session):
    """Test extraction of wrong data.
    Check the system capability of ignoring
    false/missing information."""
    assert (
        not len(extract_shared_list_from_data(WRONG_DATA, session).items) == 3
    )


def test_extract_shared_list_from_data_error_handling(session):
    """Test error handling during extraction."""
    WRONG_DATA.setlist("item-name", ["Vanilla", "Strawberries", "Coffee"])
    assert extract_shared_list_from_data(WRONG_DATA, session)


def test_check_item_is_valid():
    """Check if a wrong Item object is valid."""
    Item = namedtuple("Item", ["name", "amount", "participant"])
    item = Item(name="Bagel", amount="word", participant="John")
    assert not _check_item_is_valid(item)
