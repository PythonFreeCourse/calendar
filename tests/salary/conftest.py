from typing import Iterator

import pytest
from sqlalchemy.orm.session import Session

from app.database.models import SalarySettings, User
from app.internal.utils import create_model, delete_instance
from app.routers.salary import config


MESSAGES = {
    'create_settings': 'Already created your settings?',
    'pick_settings': 'Edit Settings',
    'edit_settings': 'Settings don\'t need editing?',
    'pick_category': 'Calculate Salary',
    'view_salary': 'Need to alter your settings?',
    'salary_calc': 'Total Salary:',
}

ROUTES = {
    'home': '/salary',
    'new': '/salary/new',
    'edit': '/salary/edit',
    'view': '/salary/view'
}

HTTP_CODES = {
    'ok': 200,
    'temp_redirect': 307,
}

CATEGORY_ID = 1
INVALID_CATEGORY_ID = 2
MONTH = '2021-01'


@pytest.fixture
def wage(session: Session, user: User) -> Iterator[SalarySettings]:
    wage = create_model(
        session,
        SalarySettings,
        user_id=user.id,
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
    delete_instance(session, wage)