from typing import Iterator

import pytest
from sqlalchemy.orm.session import Session

from app.database.models import Base, SalarySettings, User
from app.internal.utils import create_model, delete_instance
from app.routers.salary import config
from app.routers.salary.routes import router
from tests.conftest import get_test_db
from tests.conftest import test_engine

MESSAGES = {
    'create_settings': 'Already created your settings?',
    'pick_settings': 'Edit Settings',
    'edit_settings': 'Settings don\'t need editing?',
    'pick_category': 'View Salary',
    'view_salary': 'Need to alter your settings?',
    'salary_calc': 'Total Salary:',
}

ROUTES = {
    'home': router.url_path_for('salary_home'),
    'new': router.url_path_for('create_settings'),
    'edit_pick': router.url_path_for('pick_settings'),
    'edit': lambda x: router.url_path_for('edit_settings', category_id=x),
    'view_pick': router.url_path_for('pick_category'),
    'view': lambda x: router.url_path_for('view_salary', category_id=x),
}

CATEGORY_ID = 1
INVALID_CATEGORY_ID = 2
ALT_CATEGORY_ID = 42
MONTH = '2021-01'


@pytest.fixture(scope='package')
def salary_session() -> Iterator[Session]:
    Base.metadata.create_all(bind=test_engine)
    session = get_test_db()
    yield session
    session.close()
    Base.metadata.drop_all(bind=test_engine)


@pytest.fixture
def salary_user(salary_session: Session):
    test_user = create_model(
        salary_session, User,
        username='test_username',
        password='test_password',
        email='test.email@gmail.com',
    )
    yield test_user
    delete_instance(salary_session, test_user)


@pytest.fixture
def wage(salary_session: Session,
         salary_user: User) -> Iterator[SalarySettings]:
    wage = create_model(
        salary_session,
        SalarySettings,
        user_id=salary_user.id,
        category_id=CATEGORY_ID,
        wage=30,
        off_day=config.SATURDAY,
        holiday_category_id=config.ISRAELI_JEWISH,
        regular_hour_basis=config.REGULAR_HOUR_BASIS,
        night_hour_basis=config.NIGHT_HOUR_BASIS,
        night_start=config.NIGHT_START,
        night_end=config.NIGHT_END,
        night_min_len=config.NIGHT_MIN_LEN,
        first_overtime_amount=config.FIRST_OVERTIME_AMOUNT,
        first_overtime_pay=config.FIRST_OVERTIME_PAY,
        second_overtime_pay=config.SECOND_OVERTIME_PAY,
        week_working_hours=config.WEEK_WORKING_HOURS,
        daily_transport=config.STANDARD_TRANSPORT,
    )
    yield wage
    delete_instance(salary_session, wage)
