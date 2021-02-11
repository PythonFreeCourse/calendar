import pytest

from app.routers.event import create_shared_list


TEST_SHARED_LISTS = [
    {'title': 'Choco list', 'items': [{'name': 'Chocolate',
                                      'amount': 2,
                                      'participant': 'Elior',
                                      'notes': 'Maltesers are awesome!'}]},
    {'items': [{'name': 'Notebooks',
               'amount': 2.5,
               'participant': 'Efrat'}]}
]


@pytest.mark.parametrize("test_list", TEST_SHARED_LISTS)
def test_create_shared(test_list, session):
    shared_list = create_shared_list(test_list, session)
    assert (shared_list.title == test_list.get('title')
           or shared_list.title == 'Shared List')
    assert shared_list.items[0].name == test_list['items'][0]['name']
