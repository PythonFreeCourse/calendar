from typing import Dict

import pytest
from sqlalchemy.orm.session import Session
from starlette.testclient import TestClient

from app.database.models import Event
from app.routers import meds
from tests.meds.test_internal import create_test_form, WEB_FORM


PYLENDAR = [
    (WEB_FORM, True),
    (create_test_form(form_dict=True, end='1985-10-26'), False),
]


def test_meds_page_returns_ok(meds_test_client: TestClient) -> None:
    path = meds.router.url_path_for('medications')
    response = meds_test_client.get(path)
    assert response.ok


@pytest.mark.parametrize('form, pylendar', PYLENDAR)
def test_meds_send_form_success(meds_test_client: TestClient, session: Session,
                                form: Dict[str, str], pylendar: bool) -> None:
    assert session.query(Event).first() is None
    path = meds.router.url_path_for('medications')
    response = meds_test_client.post(path, data=form, allow_redirects=True)
    assert response.ok
