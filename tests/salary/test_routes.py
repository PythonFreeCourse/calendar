from unittest import mock

from fastapi import status
import pytest
from requests.sessions import Session
from starlette.testclient import TestClient

from app.database.models import SalarySettings, User
from app.internal.utils import delete_instance
from app.routers.salary import routes, utils
from tests.salary import conftest
from tests.salary.test_utils import get_event_by_category

PATHS = [
    (conftest.ROUTES['new']),
    (conftest.ROUTES['edit_pick']),
    (conftest.ROUTES['edit'](conftest.CATEGORY_ID)),
    (conftest.ROUTES['view_pick']),
    (conftest.ROUTES['view'](conftest.CATEGORY_ID)),
]

EMPTY_PICKS = [
    (conftest.ROUTES['edit_pick']),
    (conftest.ROUTES['view_pick']),
]

CATEGORY_PICK = [
    (conftest.ROUTES['edit_pick'], conftest.MESSAGES['edit_settings']),
    (conftest.ROUTES['view_pick'], conftest.MESSAGES['view_salary']),
]

INVALID = [
    (conftest.ROUTES['edit'](conftest.ALT_CATEGORY_ID),
     conftest.MESSAGES['pick_settings']),
    (conftest.ROUTES['view'](conftest.ALT_CATEGORY_ID),
     conftest.MESSAGES['pick_category']),
    (conftest.ROUTES['edit'](conftest.INVALID_CATEGORY_ID),
     conftest.MESSAGES['pick_settings']),
    (conftest.ROUTES['view'](conftest.INVALID_CATEGORY_ID),
     conftest.MESSAGES['pick_category']),
]


def get_current_user(salary_session: Session) -> User:
    user = salary_session.query(User).filter_by(id=2).first()
    return user


def test_get_user_categories() -> None:
    # Code revision required after categories feature is added
    categories = {
        1: 'Workout',
        17: 'Flight',
        42: 'Going to the Movies',
        666: 'Lucy\'s Inferno',
    }
    assert routes.get_user_categories() == categories


def test_get_holiday_categories() -> None:
    # Code revision required after holiday times feature is added
    holidays = {
        1: 'Israel - Jewish',
        3: 'Iraq - Muslim',
        17: 'Cuba - Santeria',
        666: 'Hell - Satanist',
    }
    assert routes.get_holiday_categories() == holidays


def test_get_salary_categories_empty(salary_session: Session,
                                     salary_user: User) -> None:
    # Code revision required after categories feature is added
    assert routes.get_salary_categories(salary_session, salary_user.id) == {}


def test_get_salary_categories(salary_session: Session,
                               wage: SalarySettings) -> None:
    # Code revision required after categories feature is added
    assert wage.category_id in routes.get_salary_categories(salary_session,
                                                            wage.user_id, True)


def test_get_salary_categories_new(salary_session: Session,
                                   wage: SalarySettings) -> None:
    # Code revision required after categories feature is added
    assert wage.category_id not in routes.get_salary_categories(
        salary_session, wage.user_id, False)


@pytest.mark.parametrize('path', PATHS)
def test_pages_respond_ok(salary_test_client: TestClient,
                          wage: SalarySettings, path: str) -> None:
    response = salary_test_client.get(path)
    assert response.ok


def test_home_page_redirects_to_new(
        salary_test_client: TestClient) -> None:
    response = salary_test_client.get(conftest.ROUTES['home'])
    assert response.ok
    assert conftest.MESSAGES['create_settings'] in response.text


@mock.patch('app.routers.salary.routes.get_current_user',
            new=get_current_user)
def test_home_page_redirects_to_view(salary_test_client: TestClient,
                                     wage: SalarySettings) -> None:
    response = salary_test_client.get(conftest.ROUTES['home'])
    assert response.ok
    assert conftest.MESSAGES['pick_category'] in response.text


@mock.patch('app.routers.salary.routes.get_current_user',
            new=get_current_user)
def test_create_settings(salary_test_client: TestClient,
                         salary_session: Session, salary_user: User) -> None:
    category_id = conftest.CATEGORY_ID
    assert utils.get_settings(salary_session, salary_user.id,
                              category_id) is None
    data = {
        'category_id': category_id,
        'wage': utils.DEFAULT_SETTINGS.wage,
        'off_day': utils.DEFAULT_SETTINGS.off_day,
        'holiday_category_id': utils.DEFAULT_SETTINGS.holiday_category_id,
        'regular_hour_basis': utils.DEFAULT_SETTINGS.regular_hour_basis,
        'night_hour_basis': utils.DEFAULT_SETTINGS.night_hour_basis,
        'night_start': utils.DEFAULT_SETTINGS.night_start,
        'night_end': utils.DEFAULT_SETTINGS.night_end,
        'night_min_len': utils.DEFAULT_SETTINGS.night_min_len,
        'first_overtime_amount': utils.DEFAULT_SETTINGS.first_overtime_amount,
        'first_overtime_pay': utils.DEFAULT_SETTINGS.first_overtime_pay,
        'second_overtime_pay': utils.DEFAULT_SETTINGS.second_overtime_pay,
        'week_working_hours': utils.DEFAULT_SETTINGS.week_working_hours,
        'daily_transport': utils.DEFAULT_SETTINGS.daily_transport,
    }
    response = salary_test_client.post(
        conftest.ROUTES['new'], data=data, allow_redirects=True)
    assert response.ok
    assert conftest.MESSAGES['view_salary'] in response.text
    settings = utils.get_settings(salary_session, salary_user.id, category_id)
    assert settings
    delete_instance(salary_session, settings)


@pytest.mark.parametrize('path', EMPTY_PICKS)
def test_empty_category_pick_redirects_to_new(salary_test_client: TestClient,
                                              path: str) -> None:
    response = salary_test_client.get(path)
    assert any(temp.status_code == status.HTTP_307_TEMPORARY_REDIRECT
               for temp in response.history)


@pytest.mark.parametrize('path, message', CATEGORY_PICK)
@mock.patch('app.routers.salary.routes.get_current_user',
            new=get_current_user)
def test_pick_category(salary_test_client: TestClient, wage: SalarySettings,
                       path: str, message: str) -> None:
    data = {'category_id': wage.category_id}
    response = salary_test_client.post(path, data=data, allow_redirects=True)
    assert message in response.text


@mock.patch('app.routers.salary.routes.get_current_user',
            new=get_current_user)
def test_edit_settings(salary_test_client: TestClient, salary_session: Session,
                       wage: SalarySettings) -> None:
    category_id = wage.category_id
    settings = utils.get_settings(salary_session, wage.user_id, category_id)
    route = conftest.ROUTES['edit'](category_id)
    data = {
        'wage': wage.wage + 1,
        'off_day': wage.off_day,
        'holiday_category_id': wage.holiday_category_id,
        'regular_hour_basis': wage.regular_hour_basis,
        'night_hour_basis': wage.night_hour_basis,
        'night_start': wage.night_start,
        'night_end': wage.night_end,
        'night_min_len': wage.night_min_len,
        'first_overtime_amount': wage.first_overtime_amount,
        'first_overtime_pay': wage.first_overtime_pay,
        'second_overtime_pay': wage.second_overtime_pay,
        'week_working_hours': wage.week_working_hours,
        'daily_transport': wage.daily_transport,
    }
    response = salary_test_client.post(route, data=data, allow_redirects=True)
    assert response.ok
    assert conftest.MESSAGES['view_salary'] in response.text
    assert settings != utils.get_settings(salary_session, wage.user_id,
                                          wage.category_id)


@pytest.mark.parametrize('path, message', INVALID)
@mock.patch('app.routers.salary.routes.get_current_user',
            new=get_current_user)
def test_invalid_category_redirect(
        salary_test_client: TestClient, wage: SalarySettings, path: str,
        message: str) -> None:
    response = salary_test_client.get(path)
    assert any(temp.status_code == status.HTTP_307_TEMPORARY_REDIRECT
               for temp in response.history)
    print(response.text)
    assert message in response.text


@mock.patch('app.routers.salary.routes.get_current_user',
            new=get_current_user)
@mock.patch('app.routers.salary.utils.get_event_by_category',
            new=get_event_by_category)
def test_view_salary(salary_test_client: TestClient,
                     wage: SalarySettings) -> None:
    route = (conftest.ROUTES['view'](wage.category_id))
    data = {
        'month': conftest.MONTH,
        'bonus': 1000,
        'deduction': 1000,
        'overtime': True
    }
    response = salary_test_client.post(route, data=data)
    assert response.ok
    assert conftest.MESSAGES['salary_calc'] in response.text
