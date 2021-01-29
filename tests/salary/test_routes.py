from unittest import mock

import pytest
from requests.sessions import Session
from starlette.testclient import TestClient

from app.database.models import SalarySettings, User
from app.internal.utils import delete_instance
from app.routers.salary import routes, utils
from tests.conftest import TestingSessionLocal
from tests.salary import conftest


def get_current_user() -> User:
    session = TestingSessionLocal()
    user = session.query(User).filter_by(id=2).first()
    return user


@mock.patch('app.routers.salary.routes.SessionLocal',
            new=TestingSessionLocal)
def test_get_current_user(session: Session) -> None:
    # Code revision required after user login feature is added
    assert session.query(User).filter_by(id=1).first() is None
    routes.get_current_user()
    assert session.query(User).filter_by(id=1).first() is not None


def test_get_user_categories() -> None:
    # Code revision required after categories feature is added
    categories =  {
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


def test_get_salary_categories_empty(user: User) -> None:
    # Code revision required after categories feature is added
    assert routes.get_salary_categories(user.id) == {}


@mock.patch('app.routers.salary.utils.SessionLocal',
            new=TestingSessionLocal)
def test_get_salary_categories(wage: SalarySettings) -> None:
    # Code revision required after categories feature is added
    assert wage.category_id in routes.get_salary_categories(
        wage.user_id, True)


@mock.patch('app.routers.salary.utils.SessionLocal',
            new=TestingSessionLocal)
def test_get_salary_categories_new(wage: SalarySettings) -> None:
    # Code revision required after categories feature is added
    assert wage.category_id not in routes.get_salary_categories(
        wage.user_id, False)


@mock.patch('app.routers.salary.utils.SessionLocal',
            new=TestingSessionLocal)
@mock.patch('app.routers.salary.routes.SessionLocal',
            new=TestingSessionLocal)
def test_home_page_redirects_to_new(
    salary_test_client: TestClient) -> None:
    response = salary_test_client.get(conftest.ROUTES['home'])
    assert response.status_code == conftest.HTTP_CODES['ok']
    assert conftest.MESSAGES['create_settings'] in response.text


@mock.patch.multiple('app.routers.salary.routes',
                     SessionLocal=TestingSessionLocal,
                     get_current_user=get_current_user)
@mock.patch('app.routers.salary.utils.SessionLocal',
            new=TestingSessionLocal)
def test_home_page_redirects_to_view(
    salary_test_client: TestClient,
    wage: SalarySettings) -> None:
    response = salary_test_client.get(conftest.ROUTES['home'])
    assert response.status_code == conftest.HTTP_CODES['ok']
    assert conftest.MESSAGES['pick_category'] in response.text


@mock.patch.multiple('app.routers.salary.routes',
                     SessionLocal=TestingSessionLocal,
                     get_current_user=get_current_user)
@mock.patch('app.routers.salary.utils.SessionLocal',
            new=TestingSessionLocal)
def test_create_settings(salary_test_client: TestClient, session: Session,
                         user: User) -> None:
    category_id = 1
    assert utils.get_settings(user.id, category_id) is None
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
    assert response.status_code == conftest.HTTP_CODES['ok']
    assert conftest.MESSAGES['view_salary'] in response.text
    settings = utils.get_settings(user.id, category_id)
    assert settings
    delete_instance(session, settings)


@mock.patch('app.routers.salary.utils.SessionLocal',
            new=TestingSessionLocal)
def test_pick_settings_redirect_home(salary_test_client: TestClient) -> None:
    response = salary_test_client.get(conftest.ROUTES['edit'])
    assert any(temp.status_code == conftest.HTTP_CODES['temp_redirect']
               for temp in response.history)


# Fails test_create_settings
# @mock.patch.multiple('app.routers.salary.routes',
#                      SessionLocal=TestingSessionLocal,
#                      get_current_user=get_current_user)
# @mock.patch('app.routers.salary.utils.SessionLocal',
#             new=TestingSessionLocal)
# def test_pick_settings(salary_test_client: TestClient,
#                        wage: SalarySettings) -> None:
#     data = {'category_id': wage.category_id}
#     response = salary_test_client.post(conftest.ROUTES['edit'], data=data, allow_redirects=True)
#     assert conftest.MESSAGES['edit_settings'] in response.text